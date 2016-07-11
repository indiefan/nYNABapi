import codecs
import inspect
import json
import os
import sys
from collections import namedtuple
from datetime import datetime

import configargparse
import io
from jsontableschema.exceptions import InvalidSchemaError, InvalidCastError, ConversionError
from jsontableschema.model import SchemaModel

from pynYNAB.Client import clientfromargs
from pynYNAB.config import get_logger, test_common_args
from pynYNAB.schema.budget import Transaction
from pynYNAB.scripts.common import get_account, get_subcategory, get_payee, transaction_dedup

scriptsdir = os.path.dirname(os.path.abspath(__file__))
schemas_dir = os.path.join(scriptsdir, 'csv_schemas')


def csvimport_main():
    print('pynYNAB CSV import')
    """Manually import a CSV into a nYNAB budget"""
    parser = configargparse.getArgumentParser('pynYNAB')
    parser.description = inspect.getdoc(csvimport_main)
    parser.add_argument('csvfile', metavar='CSVpath', type=str,
                        help='The CSV file to import')
    parser.add_argument('schema', metavar='schemaName', type=str,
                        help='The CSV schema to use (see csv_schemas directory)')
    parser.add_argument('accountname', metavar='AccountName', type=str, nargs='?',
                        help='The nYNAB account name  to use')
    parser.add_argument('--encoding', metavar='Encoding', type=str, default='utf-8',
                        help='The encoding to read the CSV file')
    parser.add_argument('-import-duplicates', action='store_true',
                        help='Forces the import even if a duplicate (same date, account, amount, memo, payee) is found')

    args = parser.parse_args()
    test_common_args(args)

    if not os.path.exists(args.csvfile):
        get_logger().error('input CSV file does not exist')
        exit(-1)

    do_csvimport(args)


def transaction_list(args, client=None):
    if client is None:
        client = clientfromargs(args)
    logger = get_logger(args)

    logger.debug('selected schema %s' % (args.schema,))
    if os.path.exists(args.schema):
        schemafile = args.schema
    else:
        schemafile = os.path.join(schemas_dir, args.schema + '.json')
        if not os.path.exists(schemafile):
            logger.error('This schema doesn''t exist in csv_schemas')
            exit(-1)
    try:
        schema = SchemaModel(schemafile, case_insensitive_headers=True)
        with open(schemafile, 'r') as sf:
            schemacontent = json.load(sf)
            try:
                nheaders = schemacontent['nheaders']
            except KeyError:
                nheaders = 1
    except InvalidSchemaError:
        logger.error('Invalid CSV schema')
        raise
    logger.debug('schema headers %s' % schema.headers)

    if 'account' not in schema.headers and args.accountname is None:
        logger.error('This schema does not have an account column and no account name was provided')
        exit(-1)

    if 'account' not in schema.headers:
        entities_account_id = get_account(client,args.accountname).id

    if ('inflow' in schema.headers and 'outflow' in schema.headers) or 'amount' in schema.headers:
        pass
    else:
        logger.error('This schema doesn''t provide an amount column or (inflow,outflow) columns')
        exit(-1)

    csvrow = namedtuple('CSVrow', field_names=schema.headers)
    transactions = []

    imported_date = datetime.now().date()

    transactions_dedup = map(transaction_dedup, client.budget.be_transactions)

    if sys.version[0] == '2':
        from backports import csv
    elif sys.version[0] == '3':
        import csv

    get_logger(args).debug('OK starting the import from %s ' % os.path.abspath(args.csvfile))

    def open_file(filepath,encoding):
        if sys.version[0] == '2':
            return io.open(filepath, mode='r',encoding=encoding)
        elif sys.version[0] == '3':
            return open(filepath, mode='r', encoding=encoding)

    with open_file(args.csvfile,args.encoding) as inputfile:
        for i in range(nheaders):
            inputfile.readline()
        for row in csv.reader(inputfile):
            logger.info('read line %s' % row)
            try:
                result = csvrow(*list(schema.convert_row(*row, fail_fast=True)))
            except InvalidCastError as e:
                logger.warning('Invalid Cast Error %s, ignoring line'%e)
                continue
            except ConversionError as e:
                logger.warning('Conversion Error %s, ignoring line' % e)
                continue
            if 'account' in schema.headers:
                entities_account_id = get_account(client,result.account).id
            if 'inflow' in schema.headers and 'outflow' in schema.headers:
                amount = result.inflow - result.outflow
            elif 'amount' in schema.headers:
                amount = result.amount

            if 'category' in schema.headers and result.category:
                master,sub=result.category.split(':')
                entities_subcategory_id = get_subcategory(client,master,sub).id
            else:
                entities_subcategory_id = None
            if 'payee' in schema.headers:
                imported_payee = result.payee
            else:
                imported_payee = ''
            entities_payee_id = get_payee(client,imported_payee).id
            if 'memo' in schema.headers:
                memo = result.memo
            else:
                memo = ''

            transaction = Transaction(
                entities_account_id=entities_account_id,
                amount=float(amount),
                date=result.date,
                entities_payee_id=entities_payee_id,
                entities_subcategory_id=entities_subcategory_id,
                imported_date=imported_date,
                imported_payee=imported_payee,
                memo=memo,
                source="Imported"
            )

            if args.import_duplicates or (not transaction_dedup(transaction) in transactions_dedup):
                logger.info('Appending transaction %s ' % transaction.get_dict())
                transactions.append(transaction)
            else:
                logger.info('Duplicate transaction found %s ' % transaction.get_dict())
    return transactions


def do_csvimport(args, client=None):
    if client is None:
        client = clientfromargs(args)
    client.add_transactions(transaction_list(args,client))


if __name__ == "__main__":
    csvimport_main()
