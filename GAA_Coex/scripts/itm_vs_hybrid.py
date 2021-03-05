from reference_models.propagation import wf_hybrid
from reference_models.propagation import wf_itm

if __name__ == '__main__':
    lat1 = 32.7235017497
    indoor = True
    lng1 = -117.162408646
    agl1 = 3
    rels = [-1, 0.5]
    rt = "RURAL"

    lat2 = 32.74049506692264
    lng2 = -117.14025198345544
    agl2 = 1.5

    for rel in rels:
        loss_hybrid = wf_hybrid.CalcHybridPropagationLoss(lat1, lng1, agl1, lat2, lng2, agl2, cbsd_indoor=indoor, region=rt, reliability=rel)
        loss_itm = wf_itm.CalcItmPropagationLoss(lat1, lng1, agl1, lat2, lng2, agl2, cbsd_indoor=indoor, reliability=rel)

        print "Reliablity: ", rel
        print "Hybrid Loss:", loss_hybrid[0], "dbm:", 26-loss_hybrid[0]
        print "ITM Loss:", loss_itm[0], "dbm", 26-loss_itm[0]
        print

