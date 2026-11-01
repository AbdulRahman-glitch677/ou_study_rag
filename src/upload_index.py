from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="chroma_db",
    repo_id="sickeningstone/ou-study-rag-data",
    repo_type="dataset",
)
print("uploaded")