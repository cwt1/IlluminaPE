import os, sys
from collections import defaultdict
from miscBowTie import FastqReader, FastqWriter
from Bio import SeqIO

def combine_RF(fotu, rotu, ffastq, rfastq, output_prefix):
	"""
	Reads two OTU files, 1 for forward 1 for reverse
	Returns: forward otu cid --> reverse otu cid --> abundance
	"""
	seqid2otu = {}
	combo = {}
	with open(fotu) as f:
		for line in f:
			otu, rest = line.strip().split(None, 1)
			combo[otu] = defaultdict(lambda: 0) 
			for seqid in rest.split():
				if seqid.endswith('/1') or seqid.endswith('/2'):
					seqid = seqid[:-2]
				seqid2otu[seqid] = otu
	with open(rotu) as f:
		for line in f:
			otu2, rest = line.strip().split(None, 1)
			for seqid in rest.split():
				if seqid.endswith('/1') or seqid.endswith('/2'):
					seqid = seqid[:-2]
				if seqid not in seqid2otu:
					print >> sys.stderr, "{0} is missing in forward, ignore".format(seqid)
					continue
				otu1 = seqid2otu[seqid]
				combo[otu1][otu2] += 1		
		
	# now write this out as <output_prefix>.combined.{1|2}.fq
	seqdict = {}
	for r in FastqReader(rfastq):
		seqdict[r['ID']] = r

	fqw1 = FastqWriter(output_prefix + '.combined.1.fq')
	fqw2 = FastqWriter(output_prefix + '.combined.2.fq')
	fout = open(output_prefix + '.combined.abundance.txt','w')
	for r in FastqReader(ffastq):
		if r['ID'] in combo:
			for id2, abundance in combo[r['ID']].iteritems():
				newid = "{0}_{1}".format(r['ID'], id2)
				fqw1.write(r, id=newid+'/1') 
				fqw2.write(seqdict[id2], id=newid+'/2') 
				#fqw1.write(">{id}\n{seq}\n".format(seq=r.seq, id=newid+'/1'))
				#fqw2.write(">{id}\n{seq}\n".format(seq=seqdict[id2].seq, id=newid+'/2'))
				fout.write("{0}\t{1}\n".format(newid, abundance))
	fqw1.close()
	fqw2.close()
	fout.close()
	return combo

if __name__ == "__main__":
	combo = combine_RF(*sys.argv[1:])
