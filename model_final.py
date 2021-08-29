import os
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor

csv_path = os.path.join("data", "TV-2_processed.csv")
model_path = os.path.join("models", "saved_model_new")
brandless_model_path = os.path.join("models", "saved_brandless_model_new")
dataset = pd.read_csv(csv_path)
dataset = dataset.drop(['buy_from', 'img_url'], axis=1)

brand_labelencoder = LabelEncoder()
speaker_labelencoder = LabelEncoder()
size_labelencoder = LabelEncoder()
hd_labelencoder = LabelEncoder()
rating_scaler = StandardScaler()

dataset.iloc[:, 0] = brand_labelencoder.fit_transform(dataset.iloc[:, 0])
dataset.iloc[:, 1] = rating_scaler.fit_transform(
    dataset.iloc[:, 1].values.reshape(-1, 1))
dataset.iloc[:, 2] = speaker_labelencoder.fit_transform(dataset.iloc[:, 2])
dataset.iloc[:, 3] = size_labelencoder.fit_transform(dataset.iloc[:, 3])
dataset.iloc[:, 4] = hd_labelencoder.fit_transform(dataset.iloc[:, 4])

x = dataset.iloc[:, :-1]
y = dataset.iloc[:, -1]

col_transformer = ColumnTransformer(transformers=[(
    'ohe', OneHotEncoder(), [0, 2, 3, 4, 5, 6])], remainder='passthrough')
x = col_transformer.fit_transform(x)
x = x.todense()
log_y = np.log2(y)
scaler_y = StandardScaler()
y = scaler_y.fit_transform(y.values.reshape(-1, 1))


def pred_with_brand(brand, rating, speaker, size, hd, hdmi, usb):
    rating = max(rating, 3.7)
    topredict = [[brand.lower(), rating, speaker, size, hd, hdmi, usb]]
    temp = pd.DataFrame(topredict)
    temp.columns = ['Brand', 'Ratings', 'Speaker', 'Size', 'HD', 'HDMI', 'USB']
    temp.iloc[:, 0] = brand_labelencoder.transform(temp.iloc[:, 0])
    temp.iloc[:, 1] = rating_scaler.transform(
        temp.iloc[:, 1].values.reshape(-1, 1))
    temp.iloc[:, 2] = speaker_labelencoder.transform(temp.iloc[:, 2])
    temp.iloc[:, 3] = size_labelencoder.transform(temp.iloc[:, 3])
    temp.iloc[:, 4] = hd_labelencoder.transform(temp.iloc[:, 4])
    temp = col_transformer.transform(temp)
    temp = temp.todense()
    model = pickle.load(open(model_path, 'rb'))
    y_pred = model.predict(temp)
    y_pred = scaler_y.inverse_transform(y_pred)
    return_values = {"brand": brand,
                     "quality": hd,
                     "hdmi": hdmi,
                     "rating": rating,
                     "size": size,
                     "speaker": speaker,
                     "usb": usb,
                     "cost": round(y_pred[0])}
    return return_values

if __name__ == '__main__':
    prune = False
    if prune:
        # Number of trees in random forest
        n_estimators = [int(x)
                        for x in np.linspace(start=200, stop=2000, num=10)]
        # Number of features to consider at every split
        max_features = ['auto', 'sqrt']
        # Maximum number of levels in tree
        max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
        max_depth.append(None)
        # Minimum number of samples required to split a node
        min_samples_split = [2, 5, 10]
        # Minimum number of samples required at each leaf node
        min_samples_leaf = [1, 2, 4]
        # Method of selecting samples for training each tree
        bootstrap = [True, False]
        # Create the random grid
        random_grid = {'n_estimators': n_estimators,
                       'max_features': max_features,
                       'max_depth': max_depth,
                       'min_samples_split': min_samples_split,
                       'min_samples_leaf': min_samples_leaf,
                       'bootstrap': bootstrap}

        rf = RandomForestRegressor()
        grid_search = GridSearchCV(
            estimator=rf, param_grid=random_grid, cv=3, n_jobs=-1, verbose=2)

        grid_search.fit(x, y.ravel())
        print(grid_search.best_params_)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)
    regressor = RandomForestRegressor(bootstrap=True, n_estimators=200, max_features='sqrt',
                                      max_depth=90, min_samples_split=5, min_samples_leaf=1, n_jobs=-1)
    regressor.fit(x_train, y_train.ravel())
    y_pred = regressor.predict(x_test)
    ##y_pred_acc = np.exp2(y_pred)
    ##y_test_acc = np.exp2(y_test)
    y_pred_acc = scaler_y.inverse_transform(y_pred)
    y_test_acc = scaler_y.inverse_transform(y_test)
    from sklearn.metrics import mean_squared_error
    print(f'MSE is {np.sqrt(mean_squared_error(y_test_acc, y_pred_acc))}')
    pickle.dump(regressor, open(os.path.join(
        "models", "saved_model_new"), 'wb'))
