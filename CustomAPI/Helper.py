from pathlib import Path
import os

projectName = "default"
field = "open"

class Helper():


    @staticmethod
    def serializeTuple(tuple):
        return ",".join(str(x) for x in tuple)

    def getOutputFolderPath(self):
        path = Path.cwd() / "Output" / projectName
        path.mkdir(exist_ok=True)
        return path

    @staticmethod
    def gradientAppliedXLSX(df, filename, subset):
        formattedDf = df.style.background_gradient(cmap="PiYG", subset= subset)\
                                                     .highlight_null(null_color='transparent')

        path = os.path.join(Helper().getOutputFolderPath(), filename)
        formattedDf.to_excel(path, engine="openpyxl")
        return formattedDf