from chatgpt_check import analyze_contract


class TestAnalyzeContractCheck:

    # def test_chatgpt(self):

    #     src_dir = 'tests/test_chatgpt_check'

    #     with open(f"{src_dir}/0x4957295167DfA9AEC2cA40C377D0F8CC4732c7af.txt", "r", newline="\r\n") as f:
    #         src_code = "".join(f.readlines())
    #         assert analyze_contract('0x4957295167DfA9AEC2cA40C377D0F8CC4732c7af') == ('contract', src_code)

    #     with open(f"{src_dir}/0xbb9bc244d798123fde783fcc1c72d3bb8c189413.txt", "r", encoding='utf-8') as f:
    #         src_code = "".join(f.readlines())
    #         assert analyze_contract('0xbb9bc244d798123fde783fcc1c72d3bb8c189413') == ('contract', src_code)

    def test_malicious_check(self):

        src_dir = 'tests/test_chatgpt_check/malicious.txt'

        with open(f"{src_dir}") as f:
            target = "".join(f.readlines())
            analysis = analyze_contract(target)
            first_sentence = analysis.split('.')[0] + '.'

        assert first_sentence == ("This is malicious.")


    def test_not_malicious_check(self):

        src_dir = 'tests/test_chatgpt_check/not_malicious.txt'

        with open(f"{src_dir}") as f:
            target = "".join(f.readlines())
            analysis = analyze_contract(target)
            first_sentence = analysis.split('.')[0] + '.'

        assert first_sentence == ("This is not malicious.")
