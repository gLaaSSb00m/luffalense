import treelite.frontend
import treelite.compiler

model = treelite.frontend.load_xgboost_model(
    'model/Luffa Spoonge/spoonge_ensemble_XGB_model.json'
)

compiler = treelite.compiler.gcc(name='ast_native', verbose=True)
compiler.compile(model=model, dirpath='predictor', verbose=True)
print("✅ Compiled successfully!")
