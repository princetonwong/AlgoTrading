from pathlib import Path
import os
from datetime import datetime
import pandas as pd

class Helper():
    field = "open"
    folderName = ""

    def initializeFolderName(self, symbol, subtype, timerange, strategy, params, custom, prefix = None):
        if timerange:
            timerange = self.serializeTuple(timerange[0::2])
        else:
            timerange = self.get_timestamp()

        strategy = None or strategy.__name__
        params = None or self.serializeDictValues(params)

        if prefix is not None:
            self.folderName = "[{}]-{}-{} [{}] {} {} {}".format(prefix, symbol, subtype, timerange, strategy, params,
                                                                custom)
        else:
            self.folderName = "{}-{} [{}] {} {} {}".format(symbol, subtype, timerange, strategy, params, custom)

        Helper.folderName = self.folderName
        return self.folderName

    def initializeCustomFolderName(self, folderName):
        self.folderName = folderName
        Helper.folderName = self.folderName
        return self.folderName

    def generateFilePath(self, filename, extension):
        path = Path.cwd() / "Output" / self.folderName
        os.makedirs(path,exist_ok=True)
        if filename == None:
            filename = "Unknown File Name"
        finalFilePath = "{}{}".format(filename, extension)
        return os.path.join(path, finalFilePath)

    def readXLSXFromFile(self, filename):
        path = Path.cwd() / "Static"
        filenameWithExtension = filename + ".xlsx"
        finalPath = os.path.join(path, filenameWithExtension)
        df = pd.read_excel(finalPath, engine='openpyxl')
        return df

    def outputXLSX(self, df, fileName):
        path = self.generateFilePath(fileName, ".xlsx")

        df.to_excel(path, engine="openpyxl")

        return df

    def gradientAppliedXLSX(self, df, fileName, subset):
        # for col in df.select_dtypes(['datetimetz']).columns:
        #     df[col] = df[col].dt.tz_convert(None)
        formattedDf: pd.DataFrame = df.style.background_gradient(cmap="PiYG", subset= subset)\
                                                     .highlight_null(null_color='transparent')

        self.outputXLSX(formattedDf, fileName)
        return formattedDf

    def saveFig(self, figs):
        path = self.generateFilePath("kLine", ".png")
        for fig in figs:
            for f in fig:
                f.set_size_inches(10, 5)
                f.savefig(path, dpi=300)

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%m-%d %H-%M")

    @staticmethod
    def serializeTuple(tuple):
        return ",".join(str(x) for x in tuple)

    @staticmethod
    def serializeDictValues(dict):
        return ",".join(str(x) for x in dict.values())

    @staticmethod
    def getOutputFolderPath(folderName = None):
        if folderName == None:
            folderName = Helper.folderName
        path = Path.cwd() / "Output" / folderName
        path.mkdir(exist_ok=True)
        return path




