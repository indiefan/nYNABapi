from pynYNAB.Client import clientfromargs
from pynYNAB.scripts.config import parser

# used to ping the nYNAB API to check that the sync works
def test_sync():
    args = parser.parse_known_args()[0]
    client = clientfromargs(args)
    client.sync()

if __name__ == '__main__':
    test_sync()