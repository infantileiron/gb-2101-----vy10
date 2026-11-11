import csv,sys
from src.services.seed import demo_rows
if __name__=="__main__":
    writer=csv.DictWriter(sys.stdout,fieldnames=["batch_id","station","group","loss","temperature"])
    writer.writeheader();writer.writerows(demo_rows())
