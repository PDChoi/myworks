SELECT 
s.plate, s.fiberid, s.mjd, s.z, s.zwarning, 
g.h_beta_flux, g.h_beta_flux_err, 
g.h_alpha_flux, g.h_alpha_flux_err 
FROM GalSpecLine AS g 
JOIN SpecObj AS s 
ON s.specobjid = g.specobjid 
WHERE 
h_alpha_flux > h_alpha_flux_err*5 
AND h_beta_flux > h_beta_flux_err*5 
AND h_beta_flux_err > 0 
AND h_alpha_flux > 10.*h_beta_flux 
AND s.class = 'GALAXY' 
AND s.zwarning = 0 

SELECT 
sl.plate,sl.mjd,sl.fiber, 
sl.caIIKside,sl.caIIKerr,sl.caIIKmask, 
sp.fehadop,sp.fehadopunc,sp.fehadopn, 
sp.loggadopn,sp.loggadopunc,sp.loggadopn 
FROM sppLines AS sl
JOIN sppParams AS sp 
ON sl.specobjid = sp.specobjid 
WHERE 
fehadop < -3.5 
AND fehadopunc between 0.01 
and 0.5 and fehadopn > 3 
