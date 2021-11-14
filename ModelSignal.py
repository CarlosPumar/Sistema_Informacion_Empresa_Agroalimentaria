import pandas
import numpy

#scikit learn
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor

from sklearn.model_selection import train_test_split

#from sklearn. import GridSearchCV
from skopt import BayesSearchCV
from skopt.space import Real, Categorical, Integer

#Plots
from matplotlib import pyplot as plt
from matplotlib import dates as mpl_dates


from sklearn.metrics import mean_absolute_error, mean_squared_error
    
class ModelSignal:
        
    def __init__(self, data, wList = [1, 3, 6, 8]):
    
        self.__data = data
                
        self.setWList(wList)
        
        self.__initializeErrors()
        self.__initializeResults()
        
        self.__w = None
        self.__cflList = None
        self.__scores = None
        
        self.__model_params = {
            
            'Lineal': {
                'model' : LinearRegression(),
                'params' : {
                    }
                },
            
            'Ridge': {
                'model' : Ridge(),
                'params' : {
                    'alpha' : Real(0.01, 10, prior='log-uniform'),
                    'tol' : Real(0.0001, 0.01, prior='log-uniform'),
                    'max_iter' : Integer(200, 2000)
                    }
                },
            
            'Neuronal_network': {
                'model' : MLPRegressor(learning_rate='invscaling'),
                'params' : {
                    'max_iter' : Integer(500, 2000),
                    'hidden_layer_sizes' : Integer(10, 750),
                    'activation' : Categorical(['logistic', 'relu']),
                    'alpha' : Real(0.0001, 0.01, prior='log-uniform')
                    }
                },
        
            'Random_forest' : {
                'model' : RandomForestRegressor(),
                'params' : {
                    'n_estimators' : Integer(10, 200),
                    'max_depth' : Integer(10, 200)
                    }
                }
            }
        
    def execute(self):        
        print('### EXECUTING ###')
        print('\n\n')
        
        first = True
        self.__cflList = {}
                            
        scores = {}
                
        for w in self.__wList:
            
            print(' - - W = ', w)
                            
            self.treatData()
            
            X, y = self.getData(w)
            
            X_test = X[1]
            y_test = y[1]
            
            X = X[1:]
            y = y[1:]
            
            X = pandas.concat(X)
            y = pandas.concat(y)
            
            X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.3, random_state=42)
                                
            cflList = {}
            
            for model_name, mp in self.__model_params.items():
                
                if model_name != 'Lineal':
                    print(' - - - training', model_name)
                    
                    cfl = BayesSearchCV(mp['model'], mp['params'], n_jobs= -1)
                    cfl.fit(X_train, y_train)
                    scores[model_name] = cfl.best_params_
                else:
                    scores[model_name] = None
                
            cflList =  self.__createCflList(scores, X_train, y_train)
            predicts = self.__predicts(cflList, X_val)
            
            self.__errors[w] = self.__getErrors(predicts, y_val)
                            
            for model_name, error in self.__errors[w].items():
        
                if first == True or self.__cflList[model_name]['mae'] > error['mae']:
                    
                    dic = {'cfl':cflList[model_name], 
                           'w':w,
                           'scores':scores[model_name],
                           'mae':error['mae']}
                    
                    self.__cflList[model_name] = dic
                    
            first = False
            
        print('\n')
        
        self.__get_final_model()
        
        
        #Predcits son las previsiones, puedes crear un pandas y hacer que devuelva eso la funcion
        predicts = {}
        
        for name, model in self.__cflList.items():
            
            w = model['w']
            
            X, y = self.getData(w)
            
            X_test = X[1]
            y_test = y[1]
            
            predicts[name] = model['cfl'].predict(X_test)
            
            
        errores = self.__getErrors(predicts, y_test)
        print(errores)
        
    

    def __get_final_model(self):
        
        for name, model in self.__cflList.items():
            
            w = model['w']
            scores = model['scores']
            
            X, y = self.getData(w)
            
            X = X[:1]
            y = y[:1]
            
            X = pandas.concat(X)
            y = pandas.concat(y)
            
            if name == 'Lineal':

                #Lineal
                cflLineal = LinearRegression().fit(X, y)
                
                self.__cflList[name]['cfl'] = cflLineal
                
            elif name == 'Ridge':
                
                max_iter = scores['max_iter']
                tol = scores['tol']        
                alpha = scores['alpha']        
        
                
                cflRidge = Ridge(max_iter=max_iter,
                                 tol=tol,
                                 alpha=alpha
                                 ).fit(X, y)
                    
                self.__cflList[name]['cfl'] = cflRidge
                
            elif name == 'Neuronal_network':
                
                alpha = scores['alpha']
                hidden_layer_sizes = scores['hidden_layer_sizes']
                activation = scores['activation']
                max_iter = scores['max_iter']
                
                cflNeu = MLPRegressor(learning_rate='invscaling', 
                                      alpha = alpha, 
                                      hidden_layer_sizes=hidden_layer_sizes, 
                                      activation = activation, 
                                      max_iter=max_iter
                                      ).fit(X, y)
                
                self.__cflList[name]['cfl'] = cflNeu
                
            elif name == 'Random_forest':
                
                n_estimators = scores['max_depth']
                max_depth = scores['max_depth']
        
                cflRF = RandomForestRegressor(n_estimators=n_estimators, 
                                       max_depth=max_depth
                                      ).fit(X, y)
                
                self.__cflList[name]['cfl'] = cflRF
                
                
    def __getErrors(self, predicts, y):
        
        errors = {}
        
        for name, predict in predicts.items():
            error = {}
            error['mae'] = mean_absolute_error(y, predict)
            error['mse'] = mean_squared_error(y, predict)
            errors[name] = error
        
        return errors
        
    def plotPredReal(self):
        
        y1 = self.__pred.to_numpy()
        y2 = self.__y_test.to_numpy()
        
        x = numpy.arange(len(y1))
    
        #Grafica
        plt.plot(y1, x, linestyle='solid')
        plt.style.use('seaborn')
        
        plt.plot(y2, x, linestyle='solid')
        plt.style.use('red')
    
        plt.show()
        
    def __buildLaggedFeatures(self, s,lag=2,dropna=True):
    
        if type(s) is pandas.DataFrame:
            new_dict={}
            for col_name in s:
                new_dict[col_name]=s[col_name]
                # create lagged Series
                for l in range(1,lag+1):
                    new_dict['%s_lag%d' %(col_name,l)]=s[col_name].shift(l)
            res=pandas.DataFrame(new_dict,index=s.index)
        
        elif type(s) is pandas.Series:
            the_range=range(lag+1)
            res=pandas.concat([s.shift(i) for i in the_range],axis=1)
            res.columns=['lag_%d' %i for i in the_range]
        else:
            print('Only works for DataFrame or Series')
            return None
        if dropna:
            return res.dropna()
        else:
            return res   
        
        
    def treatData(self):
        
        newData = []
        
        # Missings ---
        for data in self.__data:
            
            columns = self.__data[0].columns
            
            data = data.to_numpy()
            # data = data[:,1:]
            
            i = 0
            while i < len(data):
                j = 1
                while j < len(data[0]):
                    
                    if numpy.isnan(data[i][j]) == True:
                        
                        if i+1 < len(data) and numpy.isnan(data[i-1][j]) == False and numpy.isnan(data[i+1][j]) == False:
                            data[i][j] = ( data[i-1][j] + data[i+1][j] ) / 2
                        else:
                            data = numpy.delete(data, i, 0)
                            
                            if i < len(data):
                                j=0
                            else:
                                j = len(data[0])
                    j+=1
                i+=1
            
            newData.append(pandas.DataFrame(data, columns = columns))
            
        self.__data = newData

        
    def getData(self, w):
        
        X = []
        y = []
                
        for row in self.__data:
            
            numUntilFirstProduction = self.countUntilFirstProduction(row['recolecta'])
            
            y_append = pandas.DataFrame(row['recolecta'])
            y_append = y_append.set_index(row['fecha'])
            
            y.append(y_append.iloc[numUntilFirstProduction:])
            row = row.set_index('fecha',drop=True)
            lagDataFrame = self.__buildLaggedFeatures(row, lag=w, dropna=False)
            X.append(lagDataFrame.iloc[numUntilFirstProduction-1:-1])
              
        return X, y
    
    def countUntilFirstProduction(self, array):
        
        i = 0
        stop = False
        
        while stop == False:
            
            if array[i] != 0:
                stop = True
            else:
                i+=1
                
        return i
        
    def __createCflList(self, scores, X, y):
        
        #Lineal
        cflLineal = LinearRegression().fit(X, y)
        
        ### Ridge 
        max_iter = scores['Ridge']['max_iter']
        tol = scores['Ridge']['tol']        
        alpha = scores['Ridge']['alpha']        

        
        cflRidge = Ridge(max_iter=max_iter,
                         tol=tol,
                         alpha=alpha
                         ).fit(X, y)
        
        ### Neuronal Network
        alpha = scores['Neuronal_network']['alpha']
        hidden_layer_sizes = scores['Neuronal_network']['hidden_layer_sizes']
        activation = scores['Neuronal_network']['activation']
        max_iter = scores['Neuronal_network']['max_iter']
        
        cflNeu = MLPRegressor(learning_rate='invscaling', 
                              alpha = alpha, 
                              hidden_layer_sizes=hidden_layer_sizes, 
                              activation = activation, 
                              max_iter=max_iter
                              ).fit(X, y)
        
        ### Random Forest
        n_estimators = scores['Random_forest']['max_depth']
        max_depth = scores['Random_forest']['max_depth']
        
        cflRF = RandomForestRegressor(n_estimators=n_estimators, 
                                       max_depth=max_depth
                                      ).fit(X, y)
        
        return {'Lineal':cflLineal, 'Ridge':cflRidge, 'Neuronal_network':cflNeu, 'Random_forest':cflRF}
    
    
    def __predicts(self, cflList, X):
        
        predicts = {}
        
        for name, cfl in cflList.items():
        
            predict = cfl.predict(X)
            predicts[name] = predict
        
        return predicts
    
    def __initializeErrors(self):
        
        self.__errors = {}
        
    def __initializeResults(self):
        self.__results = {}
            
    def __initializeFeatureSelection(self):
        
        self.__featuresSelector = {}
        
        for w in self.getWList():
            self.__featuresSelector[w] = None
            
    ### GETTERS && SETTERS ###    

    def getWList(self):
        return self.__wList 
    
    def setWList(self, wList):
        self.__wList = wList
        
    def getW(self):
        return self.w
        
    def getCflList(self):
        return self.__cflList

    def setCflList(self, cflList):
        self.__cflList = cflList
    
    def getScores(self):
        return self.__scores

