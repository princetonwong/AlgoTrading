from pathlib import Path
import os
from datetime import datetime

projectName = "default"
field = "open"

class Helper():
    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    @staticmethod
    def serializeTuple(tuple):
        return ",".join(str(x) for x in tuple)

    @staticmethod
    def getOutputFolderPath(folderName = None):
        if folderName == None:
            folderName = projectName
        path = Path.cwd() / "Output" / folderName
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def gradientAppliedXLSX(df, fileName, subset):
        formattedDf = df.style.background_gradient(cmap="PiYG", subset= subset)\
                                                     .highlight_null(null_color='transparent')

        Helper.outputXLSX(formattedDf, folderName= Helper().getOutputFolderPath(), fileName = fileName)
        return formattedDf

    @staticmethod
    def outputXLSX(df, folderName, fileName = None):
        folderName = Helper().getOutputFolderPath(folderName)
        if fileName == None:
            fileName = "Unknown File Name"
        path = os.path.join(folderName, fileName)
        df.to_excel(path, engine="openpyxl")
        return df
