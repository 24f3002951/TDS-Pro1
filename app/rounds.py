from .models import TaskRequest
from .deployer import create_github_repo,notify_evaluation_url,push_files_to_github_repo,enable_github_pages,get_files_from_github_repo
from .llm import genereate_code_with_llm, round2_code_modification_function

async def round2(request: TaskRequest):
    try:
        updated_files = await get_files_from_github_repo(repo=request.task)
        # print (updated_files)

        updated_files = await round2_code_modification_function(files=updated_files,task_object=request)
      
        # print( updated_files)
        commit_sha = await push_files_to_github_repo(repo=request.task,files=updated_files)

        pages_reponse = await enable_github_pages(repo=request.task)

        pages_url = pages_reponse.get("pages_url")
        repo_url = pages_reponse.get("repo_url")

        payload = {
            "email": request.email,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        await notify_evaluation_url(request.evaluation_url, payload)
    except Exception as e:
        print(f"Error in background task round 2: {e}")


async def  round1(request: TaskRequest):
    try:
        repo_response = await create_github_repo(repo_name=request.task)
        repo_url = repo_response.get("html_url", "")

        files = await genereate_code_with_llm(request)

        commit_sha = await push_files_to_github_repo(repo=request.task,files=files)
        # commit_sha = await push_files_to_github_repo(repo=request.task)
        
        pages_reponse = await enable_github_pages(repo=request.task)
        pages_url = pages_reponse.get("pages_url")

        # Prepare payload
        payload = {
            "email": request.email,
            "task": request.task,
            "round": request.round,
            "nonce": request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        await notify_evaluation_url(request.evaluation_url, payload)
    except Exception as e:
        print(f"Error in background task round 1: {e}")
