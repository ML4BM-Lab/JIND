library(reticulate)
use_condaenv("jind", required=TRUE, conda="auto")
if(!require("argparse")){
  install.packages("argparse")
}
library("argparse")
py_config()
library(Seurat)
library(SeuratData)

parser <- ArgumentParser(description='Run JIND Classifier')
parser$add_argument('--path', default="/home/mohit/mohit/seurat_to_pkl", type="character",
                    help='path to store pkl files')

InstallData("panc8")
pd <- import("pandas")

data("panc8")
pancreas.list <- SplitObject(panc8, split.by = "tech")

create_files_JIND <- function(s1, s2, path){
    source <- s1
    source_mat = as.data.frame(t(as.matrix(source@assays$RNA@counts)))
    cell_labels = source$celltype
    source_mat['labels'] = cell_labels

    target <- s2
    target_mat = as.data.frame(t(as.matrix(target@assays$RNA@counts)))
    cell_labels = target$celltype
    target_mat['labels'] = cell_labels
    
    dir.create(path)
    output_path = sprintf("%s/train.pkl", path)
    py_save_object(as.data.frame(source_mat), output_path)

    output_path = sprintf("%s/test.pkl", path)
    py_save_object(as.data.frame(target_mat), output_path)
}



# pancreas.list <- pancreas.list[c("celseq", "celseq2", "fluidigmc1", "smartseq2")]
source <- pancreas.list$celseq
target <- pancreas.list$celseq2
path = args$path

create_files_JIND(source,target, path)

cmd = "python classify_JIND_R.py"
system(sprintf("%s --train_path %s/train.pkl --test_path %s/test.pkl --column labels --logt", cmd, path, path))

preds = pd$read_pickle(sprintf("%s/JIND_rawtop_0/JIND_assignmentbrftune.pkl", path))