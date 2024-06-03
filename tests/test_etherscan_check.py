from etherscan_check import check_address


class TestEtherscanCehck:

    def test_contract(self):

        src_dir = 'test_etherscan_check'

        with open(f"{src_dir}/0x4957295167DfA9AEC2cA40C377D0F8CC4732c7af.txt", "r", newline="\r\n") as f:
            src_code = "".join(f.readlines())
            assert check_address('0x4957295167DfA9AEC2cA40C377D0F8CC4732c7af') == ('contract', src_code)

        with open(f"{src_dir}/0xbb9bc244d798123fde783fcc1c72d3bb8c189413.txt", "r", encoding='utf-8') as f:
            src_code = "".join(f.readlines())
            assert check_address('0xbb9bc244d798123fde783fcc1c72d3bb8c189413') == ('contract', src_code)


    def test_wallet(self):

        assert check_address('0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5') == ('wallet', None)


    def test_error(self):

        assert check_address('0xbb9bc244d798123fde783fcc1c72d3b223b8c183339414') == ('error', None)