from pathlib import Path
import os
from datetime import datetime

projectName = "default"
field = "open"

class Helper():
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%m-%d-%H-%M")

    @staticmethod
    def serializeTuple(tuple):
        return ",".join(str(x) for x in tuple)

    @staticmethod
    def serializeDict(dict):
        return ",".join(str(x) for x in dict.values())

    @staticmethod
    def getOutputFolderPath(folderName = None):
        if folderName == None:
            folderName = projectName
        path = Path.cwd() / "Output" / folderName
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def gradientAppliedXLSX(df, fileName, subset, folderName=None):
        formattedDf = df.style.background_gradient(cmap="PiYG", subset= subset)\
                                                     .highlight_null(null_color='transparent')

        Helper.outputXLSX(formattedDf, folderName= Helper().getOutputFolderPath(folderName), fileName = fileName)
        return formattedDf

    @staticmethod
    def outputXLSX(df, folderName, fileName = None):
        folderName = Helper().getOutputFolderPath(folderName)
        if fileName == None:
            fileName = "Unknown File Name"
        path = os.path.join(folderName, fileName)
        df.to_excel(path, engine="openpyxl")
        return df

    #BT Helper
    @staticmethod
    def saveFig(figs, folderName):
        folderName = Helper().getOutputFolderPath(folderName)
        path = os.path.join(folderName, "kLine.png")
        for fig in figs:
            for f in fig:
                f.set_size_inches(10, 5)
                f.savefig(path, dpi=300)

    @staticmethod
    def getWriterOutputPath (folderName):
        folderName = Helper().getOutputFolderPath(folderName)
        path = os.path.join(folderName, "Data.csv")
        return path

    @staticmethod
    def getFolderName(symbol, subtype, timerange, strategy, params):
        if timerange:
            timerange = Helper().serializeTuple(timerange[0::2])
        else:
            timerange = Helper().get_timestamp()

        strategy = strategy.__name__
        params = Helper().serializeDict(params)

        return "{}-{} {} {} {}".format(symbol, subtype, timerange, strategy, params)
