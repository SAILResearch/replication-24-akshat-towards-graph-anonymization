from datetime import datetime

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, precision_score, accuracy_score, recall_score
from sklearn.model_selection import GridSearchCV
from sklearn_genetic import GASearchCV
from sklearn_genetic.space import Continuous, Categorical, Integer
from imblearn.combine import SMOTEENN


def load_change_metrics_df(change_metrics):
    change_metrics['defect'] = change_metrics['bugcount'] > 0
    # change_metrics['new_date'] = change_metrics['author_date'].apply(lambda x: datetime.fromtimestamp(x))

    # change_metrics = change_metrics.sort_values(by='new_date')
    # change_metrics['new_date'] = change_metrics['new_date'].apply(lambda x: x.strftime('%m-%d-%Y'))

    # change_metrics['rtime'] = (change_metrics['rtime'] / 3600) / 24
    change_metrics['age'] = (change_metrics['age'] / 3600) / 24
    change_metrics = change_metrics.reset_index()
    change_metrics = change_metrics.set_index('commit_id')

    bug_label = change_metrics['defect']

    if "tcmt" in change_metrics.columns:
        change_metrics.drop(['tcmt'], axis=1, inplace=True)
    change_metrics = change_metrics.drop(['author_date', 'defect']
                                         , axis=1)
    change_metrics = change_metrics.fillna(value=0)

    return change_metrics, bug_label


def prepare_df(df):
    change_metrics, bug_label = load_change_metrics_df(df)
    metric_list = ['la', 'ld', 'nd', 'ns', 'nf', 'ent', 'ndev', 'nuc', 'age', 'aexp', 'asexp', 'arexp']
    x_train = change_metrics[metric_list]

    return x_train, bug_label


def run_prediction_cross(train_df, test_df, optimize_rf):

    prep_train_df_x, prep_train_df_y = prepare_df(train_df)

    # SMOTE(k, random_state=, m)
    m_start_time = datetime.now()
    smo = SMOTEENN(random_state=42)
    prep_train_df_x, prep_train_df_y = smo.fit_resample(prep_train_df_x, prep_train_df_y)
    m_end_time = datetime.now()
    # print(f"SMOTEENN time - {m_end_time - m_start_time}")

    prep_test_df_x, prep_test_df_y = prepare_df(test_df)

    feats = {'bootstrap': False, 'ccp_alpha': 0.0, 'class_weight': None, 'criterion': 'gini', 'max_depth': 100,
             'max_features': 1, 'max_leaf_nodes': None, 'max_samples': None, 'min_impurity_decrease': 0.0,
             'min_samples_leaf': 1, 'min_samples_split': 2, 'min_weight_fraction_leaf': 0.0, 'n_estimators': 1400,
             'n_jobs': None, 'oob_score': False, 'random_state': None, 'verbose': 0, 'warm_start': False}
    # feats = {'bootstrap': True, 'max_depth': 100, 'max_features': 3, 'min_samples_leaf': 3, 'min_samples_split': 12,
    #          'n_estimators': 1800}
    global_model = RandomForestClassifier(**feats)

    # grid search for best hyperparameters
    m_start_time = datetime.now()
    if optimize_rf:
        print("Optimizing Random Forest")
        # param_grid = {
        #     'bootstrap': [True],
        #     'max_depth': [90, 100, 110, 120],
        #     'max_features': [1, 2],
        #     'min_samples_leaf': [3, 4, 5],
        #     'min_samples_split': [8, 10, 12],
        #     'n_estimators': [300, 1400, 1800]
        # }

        param_grid = {
                    # 'min_weight_fraction_leaf': Continuous(0.01, 0.5, distribution='log-uniform'),
                      # 'max_depth': Integer(2, 30),
                      # 'max_leaf_nodes': Integer(2, 50),
                      # "min_samples_leaf": Integer(2, 20),
                      "min_samples_split": Continuous(0, 1),
                      'n_estimators': Integer(50, 150)}


        grid_search = GASearchCV(estimator=global_model, param_grid=param_grid,
                                   cv=3, n_jobs=-1, verbose=2, scoring=roc_auc_score)
        grid_search.fit(prep_train_df_x, prep_train_df_y)

        # write best params to file
        with open('best_params.txt', 'a') as f:
            f.write(grid_search.best_params_ + '\n')
        print(grid_search.best_params_)
        global_model = grid_search.best_estimator_

    m_end_time = datetime.now()
    # print(f"Grid Search time - {m_end_time - m_start_time}")

    global_model.fit(prep_train_df_x, prep_train_df_y)

    pred = global_model.predict(prep_test_df_x)

    auc = roc_auc_score(prep_test_df_y, pred)
    f1 = f1_score(prep_test_df_y, pred)
    pre = precision_score(prep_test_df_y, pred)
    acc = accuracy_score(prep_test_df_y, pred)
    rec = recall_score(prep_test_df_y, pred)

    feat_imp = {}
    importances = global_model.feature_importances_
    sorted_indices = np.argsort(importances)[::-1]

    feat_labels = prep_train_df_x.columns

    for f in range(prep_train_df_x.shape[1]):
        feat_imp[feat_labels[sorted_indices[f]]] = importances[sorted_indices[f]]

    results_dict = {
        "auc": auc,
        "f1": f1,
        "pre": pre,
        "acc": acc,
        "rec": rec
    }

    return results_dict, {}, feat_imp, {}


# print positives and negatives
