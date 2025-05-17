class Utils:
    # AW: TODO: move this to a util/lib Class
    @staticmethod
    def layer_name_to_int(layer_name : str):
        match layer_name:
            case "Layer 0":
                return 0

            case "Layer 1":
                return 1

            case "Combined":
                return -1

            case _:
                return 0

    @staticmethod
    def testcase_name_to_int(testcase_name : str):
        if testcase_name == "User Input":
            return -1
        else:
            return int(testcase_name)
