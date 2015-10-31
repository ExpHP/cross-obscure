import puz
import sys
import argparse
import os
from functools import partial
from itertools import groupby

DEFAULT_SUFFIX = ' (obscured).txt'
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('PUZFILE', type=str, help='Across lite .puz file')
	parser.add_argument('--output', '-o', type=str, help='Output .txt path (default: replace ".puz" with %r)' % DEFAULT_SUFFIX)
	args = parser.parse_args()

	puzzle = puz.read(args.PUZFILE)

	default_output = '{}{}'.format(os.path.splitext(args.PUZFILE)[0], DEFAULT_SUFFIX)
	write_obscured(args.output or default_output, puzzle)

class ClueCell:
	def __init__(self, clue, row, col):
		self.clue = clue
		self.row = row
		self.col = col

# itertools.groupby, with the groups pre-listified.
# Normally, groupby returns the groups as iterators sharing the same underlying base iterator,
# which means things like ``list(groupby(seq, f))`` return a bunch of already-consumed iterators!
def groupby_lists(data, keyfunc):
	for k,g in groupby(data, keyfunc):
		yield k,list(g)

def get_clue_cells(puzzle, dir): #noqa
	if dir=='a':   numbering = puzzle.clue_numbering().across
	elif dir=='d': numbering = puzzle.clue_numbering().down
	else: raise ValueError
	w = puzzle.width
	return [ClueCell(x['clue'], x['cell'] // w, x['cell'] % w) for x in numbering]

# clues of a type, as list of list of str
def across_by_row(puzzle): return _organize_clues(puzzle, 'a', lambda x:x.row, lambda x:x.col)
def down_by_col(puzzle):   return _organize_clues(puzzle, 'd', lambda x:x.col, lambda x:x.row)

def _organize_clues(puzzle, dir, primarykey, secondarykey): # noqa
	# dicts {'num', 'clue', 'len', 'cell'}
	cells = get_clue_cells(puzzle, dir)
	cells = sorted(cells, key=primarykey) # sort by row
	rows = [g for (_,g) in groupby_lists(cells, primarykey)] # lists for each row
	rows = list(map(partial(sorted, key=secondarykey), rows)) # sort each row by col
	rows = [[x.clue for x in y] for y in rows] # just the clues
	return rows

def write_obscured(opath, puzzle):
	rows = across_by_row(puzzle)
	cols = down_by_col(puzzle)

	with open(opath, 'w') as f:
		def write(s='', *args):
			f.write('{}\n'.format(s%args))

		write(puzzle.title)
		write('by %s', puzzle.author)
		if puzzle.copyright:
			write(puzzle.copyright)
		write()

		if puzzle.notes.strip():
			write(puzzle.notes.strip())
			write()

		write('Shape: %s by %s', puzzle.height, puzzle.width)
		write()

		write('Across')
		for i, row in enumerate(rows, start=1):
			for j,clue in enumerate(row, start=1):
				write('A%s.%s: %s', i, j, clue)
		write()

		write('Down')
		for i, col in enumerate(cols, start=1):
			for j, clue in enumerate(col, start=1):
				write('D%s.%s: %s', i, j, clue)
		write()

def die(msg, *args):
	print(msg % args, file=sys.stderr)
	sys.exit(1)

if __name__ == '__main__':
	main()

