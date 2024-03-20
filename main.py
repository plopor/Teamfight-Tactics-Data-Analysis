from database import DataBase
from fastapi import FastAPI, Response
from typing import List
import io

app = FastAPI()
app.database = DataBase()

# Get items
@app.get('/Items')
def Items():
    return app.database.getItemDict()

# Get augments
@app.get('/Augments')
def Augments():
    return app.database.getAugmentDict()

# Get units
@app.get('/Units')
def Units():
    return app.database.getChampionDict()

# Objective 1
@app.get('/Objective1')
def TopCompositions(top: int):
    plot = app.database.getObjective1(top)

    buffer = io.BytesIO()
    plot.savefig(buffer, format='png')
    plot.close()

    return Response(buffer.getvalue(), media_type='image/png')

# Objective 2
@app.get('/Objective2')
def TopUnitSynergies(unit: str, top: int):
    plot = app.database.getObjective2(unit, top)

    buffer = io.BytesIO()
    plot.savefig(buffer, format='png')
    plot.close()

    return Response(buffer.getvalue(), media_type='image/png')

@app.get('/Objective3')
def TopCompositionAugments(comp: str, search: int):
    plot = app.database.getObjective3(comp, search)
    if plot is not None:
        buffer = io.BytesIO()
        plot.savefig(buffer, format='png')
        plot.close()

        return Response(buffer.getvalue(), media_type='image/png')
    else:
        return f"{comp} not found within the top {search} comps"

#Objective 4
@app.get('/Objective4')
def CompositionPerformanceGraph(top: int):
    plot = app.database.getObjective4(top)

    buffer = io.BytesIO()
    plot.savefig(buffer, format='png')
    plot.close()

    return Response(buffer.getvalue(), media_type='image/png')

# Objective 5
@app.post('/Objective5')
def SuggestCompositions(augments: List[str], units: List[str], items: List[str], search: int):
    plot = app.database.getObjective5(augments, units, items, search)

    buffer = io.BytesIO()
    plot.savefig(buffer, format='png')
    plot.close()

    return Response(buffer.getvalue(), media_type='image/png')

# This is commented out as the current state of the RiotAPI TFT data is empty for the top tier
# Refresh data
#@app.post('/Refresh')
#def Refresh():
    #app.database = DataBase(True)