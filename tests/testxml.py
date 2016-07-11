import xml.etree.ElementTree as ET
import os


content="""<?xml version="1.0"?>
<OFX>
    <SIGNONMSGSRSV1>
        <SONRS>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <DTSERVER>20071015021529.000[-8:PST]</DTSERVER>
            <LANGUAGE>ENG</LANGUAGE>
            <DTACCTUP>19900101000000</DTACCTUP>
            <FI>
                <ORG>MYBANK</ORG>
                <FID>01234</FID>
            </FI>
        </SONRS>
    </SIGNONMSGSRSV1>
    <BANKMSGSRSV1>
        <STMTTRNRS>
            <TRNUID>23382938</TRNUID>
            <STATUS>
                <CODE>0</CODE>
                <SEVERITY>INFO</SEVERITY>
            </STATUS>
            <STMTRS>
                <CURDEF>USD</CURDEF>
                <BANKACCTFROM>
                    <BANKID>987654321</BANKID>
                    <ACCTID>098-121</ACCTID>
                    <ACCTTYPE>SAVINGS</ACCTTYPE>
                </BANKACCTFROM>
                <BANKTRANLIST>
                    <DTSTART>20070101</DTSTART>
                    <DTEND>20071015</DTEND>
                    <STMTTRN>
                        <TRNTYPE>CREDIT</TRNTYPE>
                        <DTPOSTED>20070315</DTPOSTED>
                        <DTUSER>20070315</DTUSER>
                        <TRNAMT>200.00</TRNAMT>
                        <FITID>980315001</FITID>
                        <NAME>DEPOSIT</NAME>
                        <MEMO>automatic deposit</MEMO>
                    </STMTTRN>
                </BANKTRANLIST>
                <LEDGERBAL>
                    <BALAMT>5250.00</BALAMT>
                    <DTASOF>20071015021529.000[-8:PST]</DTASOF>
                </LEDGERBAL>
                <AVAILBAL>
                    <BALAMT>5250.00</BALAMT>
                    <DTASOF>20071015021529.000[-8:PST]</DTASOF>
                </AVAILBAL>
            </STMTRS>
        </STMTTRNRS>
    </BANKMSGSRSV1>
</OFX>
"""
with open('data.xml','w') as f:
    f.write(content)

tree=ET.parse('data.xml')

root=tree.getroot()
STMTTRNRS=tree.findall('*/STMTTRNRS')
for trns in STMTTRNRS:
    response=trns.find('STMTRS')
    print(response)


