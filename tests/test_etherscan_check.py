from etherscan_check import check_address
import time

class TestEtherscanCheck:

    def test_contract(self):
        src_dir = 'tests/test_etherscan_check'
        with open(f"{src_dir}/0x9bcCB0Dd17c1B2A62B70Ac4Bfad033a90CbA6F50.txt", "r", newline="\r\n") as f:
            src_code = "".join(f.readlines())
            src_code = "".join(src_code.split())
            result = check_address('0x9bcCB0Dd17c1B2A62B70Ac4Bfad033a90CbA6F50')
            result_type = result[0]
            result_src = "".join(result[1].split())
            assert (result_type, result_src) == ('contract', src_code)
            time.sleep(1)


    def test_wallet(self):
        assert check_address('0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5') == ('wallet', None)
        time.sleep(1)
    def test_error(self):
        assert check_address('0xbb9bc244d798123fde783fcc1c72d3b223b8c183339414') == ('error', None)
        time.sleep(1)
