import numpy as np
import scipy.io as sio
from sklearn.cross_validation import KFold

def load_dataset(dataset_nm, n_folds, lncRNA_len, mRNA_len):
    """Load data from file, do pre-processing, split it into train/test set.
    Parameters
    -----------------
    dataset_nm : string
        Name of dataset.
    n_folds : int
        Number of cross-validation folds.
    Returns
    -----------------
    datasets : list
        List contains split datasets for k-Fold cross-validation.
    """
    # load data from file
    data = sio.loadmat('./dataset/'+dataset_nm+'.mat')
    ins_fea = data['x']['data'][0,0]
    if dataset_nm.startswith('m'):
        bags_nm = data['x']['ident'][0,0]['milbag'][0,0]
    else:
        bags_nm = data['x']['ident'][0,0]['milbag'][0,0][:,0]
    bags_label = data['x']['nlab'][0,0][:,0] #- 1

    # L2 norm for musk1 and musk2
    #if dataset_nm.startswith('newsgroups') is False:
    #    mean_fea = np.mean(ins_fea, axis=0, keepdims=True)+1e-6
    #    std_fea = np.std(ins_fea, axis=0, keepdims=True)+1e-6
    #    ins_fea = np.divide(ins_fea-mean_fea, std_fea)
    
    genes_nm=data['x']['ident'][0,0]['ident'][0,0]
    # store data in bag level
    ins_idx_of_input = {}            # store instance index of input
    bag_name_of_input = []
    for id, bag_nm in enumerate(bags_nm):
        if ins_idx_of_input.has_key(bag_nm): ins_idx_of_input[bag_nm].append(id)
        else:                                ins_idx_of_input[bag_nm] = [id]
    ins_name_of_input = {}
    for id, bag_nm in enumerate(bags_nm):
        if ins_name_of_input.has_key(bag_nm): ins_name_of_input[bag_nm].append(genes_nm[id])
        else:                                 ins_name_of_input[bag_nm] = [genes_nm[id]]
    bags_fea = []
    bags_name = []
    bags_lncRNA_fea = []
    bags_mRNA_fea = []
    for bag_nm, ins_idxs in ins_idx_of_input.items():
        bag_fea = ([], [])
        bag_lncRNA_fea = ([], [])
        bag_mRNA_fea = ([], [])
        for ins_idx in ins_idxs:
            bag_fea[0].append(ins_fea[ins_idx])
            bag_fea[1].append(bags_label[ins_idx])
            bag_lncRNA_fea[0].append(ins_fea[ins_idx][0:lncRNA_len])
            bag_lncRNA_fea[1].append(bags_label[ins_idx])
            bag_mRNA_fea[0].append(ins_fea[ins_idx][lncRNA_len:lncRNA_len+mRNA_len])
            bag_mRNA_fea[1].append(bags_label[ins_idx])
        bags_fea.append(bag_fea)
        bags_lncRNA_fea.append(bag_lncRNA_fea)
        bags_mRNA_fea.append(bag_mRNA_fea)
        bags_name.append(bag_nm)

    # random select 90% bags as train, others as test
    n = len(bags_fea)
    kf = KFold(n, n_folds=n_folds, shuffle=True, random_state=0)
    datasets = []
    for train_idx, test_idx in kf:
        dataset={}
        dataset['train'] = [bags_fea[ibag] for ibag in train_idx]
        dataset['train_lncRNA'] = [bags_lncRNA_fea[ibag] for ibag in train_idx]
        dataset['train_mRNA'] = [bags_mRNA_fea[ibag] for ibag in train_idx]
        dataset['train_bags_nm'] = [bags_name[ibag] for ibag in train_idx]
        dataset['train_ins_nm'] = [ins_name_of_input[bags_name[ibag]] for ibag in train_idx]        
        dataset['test'] = [bags_fea[ibag] for ibag in test_idx]
        dataset['test_lncRNA'] = [bags_lncRNA_fea[ibag] for ibag in test_idx]
        dataset['test_mRNA'] = [bags_mRNA_fea[ibag] for ibag in test_idx]
        dataset['test_bags_nm'] = [bags_name[ibag] for ibag in test_idx]
        dataset['test_ins_nm'] = [ins_name_of_input[bags_name[ibag]] for ibag in test_idx] 
        datasets.append(dataset)
    return datasets
