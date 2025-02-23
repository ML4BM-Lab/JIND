import numpy as np
import sys, os, pdb
import pandas as pd
import argparse
import matplotlib
import matplotlib.font_manager
from matplotlib import pyplot as plt
import argparse
from datetime import datetime
import plotly.graph_objects as go
import os
from sklearn.metrics import confusion_matrix
import seaborn as sns
# Set style
sns.set(style="whitegrid")#, color_codes=True)


np.random.seed(0)

parser = argparse.ArgumentParser(description='Plot Rejection Figure')
parser.add_argument('--file', default="datasets/results_JIND.csv", type=str,
					help='path to train data frame with labels')
parser.add_argument('--metric', default="wf1", type=str,
					help='name of the metric')

def main():
	args = parser.parse_args()

	data = pd.read_csv(args.file, )
	print(data.columns)
	data_orig = data[['Dataset', 'JIND+', 'JIND', 'ACTINN', 'SVM_Rej', 'ItClust', 'Seurat-LT']]
	data = data_orig.iloc[:3]
	print(data)
	df = data.melt('Dataset', var_name='Method',  value_name=args.metric)

	plt.figure(figsize=(8,8))
	ax = sns.barplot(x=args.metric, y="Dataset", hue='Method', data=df, edgecolor=(0.2,0.2,0.2))
	# ax._legend.remove()
	ax.set_xlabel(ax.get_xlabel(), fontsize=14)
	ax.set_ylabel("", fontsize=12)
	# print(list(ax.get_xticks()))
	ax.set_xticklabels(ax.get_xticks(), fontsize=12)
	ax.set_yticklabels(ax.get_yticklabels(), fontsize=12, rotation=45, horizontalalignment='right')
	hatches = ['-', '+', 'x', '\\', '*', 'o']

	# for patch in ax.patches:
	# 	clr = patch.get_facecolor()
	# 	patch.set_edgecolor((0,0,0))

	# Loop over the bars
	ind = -1
	for i,thisbar in enumerate(ax.patches):
		# Set a different hatch for each bar
		if i % (len(data.index)) == 0:
			ind += 1
		thisbar.set_hatch(hatches[ind])

	ax.grid(b=True, which='major', color=(0.7, 0.7, 0.7), linewidth=2.0)

	plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12),fancybox=True, shadow=True, ncol=3, prop={"size":14})
	plt.tight_layout()


	path = os.path.dirname(args.file)
	plt.savefig("{}/{}_RejectionBarBatch.pdf".format(path, os.path.splitext(os.path.basename(args.file))[0]))

	plt.figure(figsize=(6,8))
	ax = sns.barplot(x="Dataset", y=args.metric, hue='Method', data=df)
	ax.set_xlabel(ax.get_xlabel(), fontsize=12)
	ax.set_ylabel(ax.get_ylabel(), fontsize=12)
	ax.set_yticklabels(ax.get_yticklabels(), fontsize=12)
	ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
	# ax._legend.remove()
	plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2),fancybox=True, shadow=True, ncol=2, prop={"size":14})
	plt.tight_layout()


	path = os.path.dirname(args.file)
	plt.savefig("{}/{}_RejectionBarVerticalBatch.pdf".format(path, os.path.splitext(os.path.basename(args.file))[0]))

	data = data_orig.iloc[3:]
	print(data)
	df = data.melt('Dataset', var_name='Method',  value_name=args.metric)

	plt.figure(figsize=(8,8))
	ax = sns.barplot(x=args.metric, y="Dataset", hue='Method', data=df, edgecolor=(0.2,0.2,0.2))
	# ax._legend.remove()
	ax.set_xlabel(ax.get_xlabel(), fontsize=14)
	ax.set_ylabel("", fontsize=12)
	# print(list(ax.get_xticks()))
	ax.set_xticklabels(ax.get_xticks(), fontsize=12)
	ax.set_yticklabels(ax.get_yticklabels(), fontsize=12, rotation=45, horizontalalignment='right')
	hatches = ['-', '+', 'x', '\\', '*', 'o']

	# for patch in ax.patches:
	# 	clr = patch.get_facecolor()
	# 	patch.set_edgecolor((0,0,0))

	# Loop over the bars
	ind = -1
	for i,thisbar in enumerate(ax.patches):
		# Set a different hatch for each bar
		if i % (len(data.index)) == 0:
			ind += 1
		thisbar.set_hatch(hatches[ind])

	ax.grid(b=True, which='major', color=(0.7, 0.7, 0.7), linewidth=2.0)

	plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12),fancybox=True, shadow=True, ncol=3, prop={"size":14})
	plt.tight_layout()


	path = os.path.dirname(args.file)
	plt.savefig("{}/{}_RejectionBarNonBatch.pdf".format(path, os.path.splitext(os.path.basename(args.file))[0]))

	plt.figure(figsize=(6,8))
	ax = sns.barplot(x="Dataset", y=args.metric, hue='Method', data=df)
	ax.set_xlabel(ax.get_xlabel(), fontsize=12)
	ax.set_ylabel(ax.get_ylabel(), fontsize=12)
	ax.set_yticklabels(ax.get_yticklabels(), fontsize=12)
	ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
	# ax._legend.remove()
	plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.2),fancybox=True, shadow=True, ncol=2, prop={"size":14})
	plt.tight_layout()


	path = os.path.dirname(args.file)
	plt.savefig("{}/{}_RejectionBarVerticalNonBatch.pdf".format(path, os.path.splitext(os.path.basename(args.file))[0]))






if __name__ == "__main__":
	main()
