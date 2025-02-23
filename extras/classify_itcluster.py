import ItClust as ic
import scanpy.api as sc
import os
from numpy.random import seed
from tensorflow.compat.v1 import set_random_seed
import tensorflow as tf
import pandas as pd
import numpy as np
import warnings
from scipy import sparse
os.environ["CUDA_VISIBLE_DEVICES"]="1"
warnings.filterwarnings("ignore")
import pdb
#import sys
#!{sys.executable} -m pip install 'scanpy==1.4.4.post1'
#Set seeds
seed(20180806)
np.random.seed(10)
set_random_seed(0) # on GPU may be some other default
import anndata
import pandas as pd
import argparse
from datetime import datetime
from sklearn import metrics

np.random.seed(0)

parser = argparse.ArgumentParser(description='RUN JIND')
parser.add_argument('--train_path', default="datasets/human_blood_01/train.pkl", type=str,
					help='path to train data frame with labels')
parser.add_argument('--test_path', default="datasets/human_blood_01/test.pkl", type=str,
					help='path to test data frame with labels')
parser.add_argument('--column', type=str, default='labels',
					help='column name for cell types')
parser.add_argument('--runs', type=int, default=5,
					help='column name for cell types')

def dict_mean(dict_list):
	mean_dict = {}
	for key in dict_list[0].keys():
		mean_dict[key] = np.mean([d[key] for d in dict_list])
	return mean_dict

def dict_std(dict_list):
	mean_dict = {}
	for key in dict_list[0].keys():
		mean_dict[key] = np.std([d[key] for d in dict_list])
	return mean_dict

def train_and_evaluate(adata_train, adata_test, test_labels, isfloat, res_path, run):
	os.makedirs(f"{res_path}", exist_ok=True)
	set_random_seed(run)
	clf=ic.transfer_learning_clf()
	print(isfloat)
	clf.fit(adata_train, adata_test, isfloat=isfloat, filter_cells=False, filter_genes=True, logt=True)

	pred, prob, celltype_pred=clf.predict(save_dir=res_path)
	pred = pred.set_index('cell_id')

	dic = {"cluster"+i: j[0] for i, j in celltype_pred.items()}
	probabilities = prob.rename(columns=dic)
	pred = pd.concat([probabilities, pred], axis=1)

	pred['predictions'] = [celltype_pred[str(i)][0] for i in list(pred['cluster'])]

	test_labels.index = [i+"-target" for i in list(test_labels.index)]
	pred['labels'] = list(test_labels[list(pred.index)].values)

	acc = np.sum(pred['predictions'] == pred['labels'])/(len(test_labels))
	frac_pred = len(pred) * 1.0 / len(test_labels)

	results = {'predictions': ["Unlabeled" for i in range(len(test_labels))],
				'labels': [label for label in list(test_labels)]}

	dic2 = {i: [-1]*len(test_labels) for i in sorted(list(set(test_labels)))}

	dic = {**results, **dic2}


	results = pd.DataFrame(dic, index=test_labels.index)
	results['predictions'].loc[pred.index] = list(pred['predictions'])
	for a in sorted(list(set(test_labels))):
		results[a].loc[pred.index] = list(pred[a])

	f1_scores = metrics.f1_score(results['labels'], results['predictions'], average=None)
	median_f1_score = np.median(f1_scores)
	mean_f1_score = np.mean(f1_scores)
	weighted_f1_score = metrics.f1_score(results['labels'], results['predictions'], average="weighted")

	print(np.mean(results['predictions'] == results['labels']))

	print(f"Acc: {acc} Frac Pred: {frac_pred}")
	with open(f"{res_path}/test.log", "w") as text_file:
		print(f"Acc: {acc} Frac Pred: {frac_pred} mf1 {mean_f1_score:.4f} medf1 {median_f1_score:.4f} wf1 {weighted_f1_score:.4f}", file=text_file)
	results.to_pickle(f"{res_path}/ItCluster_assignment.pkl")
	dic = {'acc': acc, 'frac_pred': frac_pred, "mf1": mean_f1_score, "medf1": median_f1_score, "wf1": weighted_f1_score}
	return dic

def main():
	tf.config.threading.set_inter_op_parallelism_threads(40)
	tf.config.threading.set_intra_op_parallelism_threads(40)
	from keras import backend as K
	K.set_session(K.tf.Session(config=K.tf.ConfigProto(intra_op_parallelism_threads=40, inter_op_parallelism_threads=40)))

	startTime = datetime.now()
	args = parser.parse_args()
	train_batch = pd.read_pickle(args.train_path)
	test_batch = pd.read_pickle(args.test_path)
	lname = args.column

	lname = "labels"
	train_batch[lname] = train_batch[lname].astype('category')
	train_batch[lname] = train_batch[lname].cat.set_categories(set(train_batch[lname]))
	train_mat = train_batch.drop(lname, axis=1).fillna(0)
	train_labels = train_batch[lname]

	test_batch[lname] = test_batch[lname].astype('category')
	test_batch[lname] = test_batch[lname].cat.set_categories(set(test_batch[lname]))
	test_mat = test_batch.drop(lname, axis=1).fillna(0)
	test_labels = test_batch[lname]

	mat = train_mat.values
	mat_round = np.rint(mat)
	error = np.mean(np.abs(mat - mat_round))
	isfloat = error != 0


	metrics = []
	for run in range(args.runs):
		dirname = os.path.dirname(args.train_path)
		res_path = f"{dirname}/ItClusterfiltercells_" + str(run)

		adata_train = anndata.AnnData(train_mat.copy())
		adata_train.obs['celltype'] = train_labels.copy()
		print(adata_train)
		# adata_train.var = pd.DataFrame(index=train_labels.index)

		adata_test = anndata.AnnData(test_mat.copy())
		print(adata_test)
		adata_test.obs['celltype'] = test_labels.copy()
		# adata_test.var = pd.DataFrame(index=test_labels.index)

		result_dic = train_and_evaluate(adata_train, adata_test, test_labels.copy(), isfloat, res_path, run)
		metrics.append(result_dic)

	avg_results = dict_mean(metrics)
	std_results = dict_std(metrics)

	res_path = f"{dirname}/ItClusterfiltercells_mean"
	os.makedirs(f"{res_path}", exist_ok=True)

	out_string = ""
	for i, j in avg_results.items():
		out_string = out_string + f" mean {i}: {j}, std {i}: {std_results[i]}"
	out_string = out_string + f" over {len(metrics)} runs"
	print(out_string)
	print("Runtime {}".format(datetime.now() - startTime))
	with open(f"{res_path}/test.log", "w") as text_file:
		print(out_string, file=text_file)
		print("Runtime {}".format(datetime.now() - startTime), file=text_file)

	


if __name__ == "__main__":
	main()
