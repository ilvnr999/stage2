import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import KFold
import joblib

def main(target_list):
    for target in target_list:
        best_R2 = [[], [], [], [], []]
        save_R2 = [[], [], [], [], []]
        save_r2 = [[], []]
        data = pd.read_excel(f'stage2_excels/{target}/{target}_merge_data.xlsx')
        y = data['nor']
        all_tags = data.columns

        for i in range(4, len(all_tags) - 2):
            for j in range(1, len(all_tags) - i - 1):
                for k in range(1, len(all_tags) - i - j):
                    tag1 = all_tags[i]
                    tag2 = all_tags[i + j]
                    tag3 = all_tags[i + j + k]
                    X = np.column_stack((data[tag1], data[tag2], data[tag3]))
                    degree = [1, 2, 3]
                    for index, num in enumerate(degree):
                        R2 = []
                        regressor = make_pipeline(PolynomialFeatures(num), LinearRegression())
                        kfold = KFold(n_splits=5, shuffle=True, random_state=4)
                        for train_index, test_index in kfold.split(X):
                            X_train, X_test = X[train_index], X[test_index]
                            y_train, y_test = y[train_index], y[test_index]
                            regressor.fit(X_train, y_train)
                            R2.append((regressor.score(X_test, y_test)))
                        if np.mean(R2) > 0:
                            tag_merge = tag1 + tag2 + tag3 + str(num)
                            best_R2[0].append(tag1)
                            best_R2[1].append(tag2)
                            best_R2[2].append(tag3)
                            best_R2[3].append(num)
                            best_R2[4].append(np.mean(R2))
                            save_r2[0].append(tag_merge)
                            save_r2[1].append(np.mean(R2))

        best3 = np.array(best_R2[4])
        b = best3.argsort()

        # 获取最高R²分数对应的特征组合和多项式度数
        best_index = b[-1]
        best_tag1 = best_R2[0][best_index]
        best_tag2 = best_R2[1][best_index]
        best_tag3 = best_R2[2][best_index]
        best_degree = best_R2[3][best_index]

        # 使用最佳组合重新训练模型
        X_best = np.column_stack((data[best_tag1], data[best_tag2], data[best_tag3]))
        best_regressor = make_pipeline(PolynomialFeatures(best_degree), LinearRegression())
        best_regressor.fit(X_best, y)

        model_filename = f'predict/{target}linear_regression_model.pkl'
        joblib.dump(best_regressor, model_filename)
        print(f"最佳模型已保存到 {model_filename}")

        print(target)
        length = len(b)
        for i in range(length - 1, -1, -1):
            save_R2[0].append(best_R2[0][b[i]])
            save_R2[1].append(best_R2[1][b[i]])
            save_R2[2].append(best_R2[2][b[i]])
            save_R2[3].append(best_R2[3][b[i]])
            save_R2[4].append(best_R2[4][b[i]])
        df = pd.DataFrame({"tag1": save_R2[0], "tag2": save_R2[1], "tag3": save_R2[2], "degree": save_R2[3], "R2": save_R2[4]})
        file_path = f'stage2_excels/{target}/{target}_kfold_three.xlsx'
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, sheet_name=target, index=False)
            print(f'{target} kflod_three saved.')

        df2 = pd.DataFrame({"tags": save_r2[0], "R2": save_r2[1]})
        file_path2 = f'stage2_excels/{target}/{target}_kfold_three_unsort.xlsx'
        with pd.ExcelWriter(file_path2, engine='openpyxl', mode='w') as writer:
            df2.to_excel(writer, sheet_name=target, index=False)
            print(f'{target} kflod_three_unsort saved.')

if __name__ == "__main__":
    # 呼叫 main 函數並傳入目標清單
    main(['PD', 'SP', 'GA'])
