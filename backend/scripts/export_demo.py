import csv,sys
from src.services.seed import demo_rows
if __name__=="__main__":
    fields=["batch_id","station","group","loss","temperature"]
    writer=csv.DictWriter(sys.stdout,fieldnames=fields,extrasaction="ignore")
    writer.writeheader();writer.writerows(demo_rows())
