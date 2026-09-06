from pathlib import Path
from dataclasses import replace
from datetime import date
from sleeperplan.config import read_json, parse_job
from sleeperplan.model import Piece

ROOT=Path(__file__).resolve().parents[1]
TODAY=date(2026,9,6)

def inputs():
    return read_json(ROOT/'examples/neighbour.json'),read_json(ROOT/'catalogues/wickes-2026-09-06.json')

def job():
    return parse_job(*inputs())

def piece(length,number=0):
    return Piece(f'p{number}','bed',1,'S','X',0,0,0,length,100,200,True)
