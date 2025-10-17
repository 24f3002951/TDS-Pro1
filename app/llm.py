import logging
from typing import List
from pydantic_ai import Agent
from .models import TaskRequest,FileContext

# Configure module-level logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)



async def genereate_code_with_llm(request: TaskRequest) -> List[FileContext]:

     # Prepare brief and attachment context
    attachments_text = ""
    if request.attachments and len(request.attachments) > 0:
        attachments_text = "\nAttachments:\n" + "\n".join([f"- {att.name}: {att.url[:80]}..." for att in request.attachments])
    else:
        attachments_text = "\n(No attachments were provided with the request)"

    prompt = f"""
Generate a complete static website project that is deployable on GitHub Pages.

Brief: {request.brief}

attachments (if any): {attachments_text}

Checks to be satisfied:
{f"{request.checks}" if getattr(request, "checks", None) else "(No explicit checks provided)"}


Requirements:
- Use the attachments provided (if any). For example, if a CSV file, image, or data file is attached,
  the generated site should correctly reference and use it in the codebase.
- Use data URIs as the source for attachments when embedding or referencing them (e.g., <img src="data:image/png;base64,..."> or fetch inline encoded data directly from JS).
- If attachments are present, they should be used within the project logically matching the task description.
- Provide all files necessary for deployment including at least an index.html.
- Write a thorough README.md that includes:
 -  the exact provided brief for the code generation  with the heading 'main goal' 
  - Project summary
  - Setup instructions for GitHub Pages
  - Usage guide
  - Explanation of the main code/files
  - License information (use MIT)
- Carefully read the provided "checks" section. Each listed check represents a requirement that must be fulfilled by the project files and behavior. 
- Checks can include both human-readable and programmatic JavaScript expressions.
- Implement all behaviors required so that JavaScript-based checks evaluate as true when tested.
- For checks beginning with `js:`:
  - Ensure your HTML, CSS, and JavaScript code produces behavior consistent with the JS expressions listed.
  - Implement any specified DOM updates, calculations, links, or asynchronous logic needed.
- Produce the project in such a way that every listed check passes successfully when evaluated automatically by test scripts or human reviewers.
- The project must follow industry standards for static GitHub Pages hosting.
- Return the project as a list of files with filenames and file contents.
- All code should be modern and ready to deploy without modification.
Output format:
Return only a JSON array of objects where each object has:
- "file_name": string
- "file_content": string
"""

    system_prompt = """
You are a highly experienced senior developer specializing in creating GitHub Pages-ready static websites.

Your goal is to produce a production-ready project based on the provided task brief and optional attachments.
The user may include one or more attachments, such as images, CSV data files, or other static assets encoded as Data URIs.


Specifically, ensure you do the following:

1. Process the task brief carefully to understand the required site behavior and structure.
2. If attachments are provided:
   - Treat them as first-class project assets.
   - Use `data:` URLs where appropriate (for images, CSV, JSON, etc.).
   - If a CSV or data file is attached, the project should load and use it accordingly in the site logic.
   - If images are attached, include them visually or reference them as part of the static content.
3. Create all necessary files to fully deploy a static website on GitHub Pages, including but not limited to:
   - index.html (the homepage)
   - any required CSS, JS, or asset files
   - configuration files (e.g., CNAME, if needed)
4. Write a complete, professional README.md file containing:
   - A clear project summary describing what the site does
   - Setup instructions to deploy the project on GitHub Pages step-by-step
   - Usage instructions, explaining how to use the website
   - Explanation of the key code files and their purpose
   - License information, applying the MIT license in standard format
5. Ensure all source code and resources are clean, properly structured, and follow modern best practices
6. Ensure the code Strictly fulfills every check listed in "checks" section . "checks" = explicit criteria the generated site will be tested against (either human-readable or
     programmatic checks such as JavaScript expressions beginning with `js:`).
     - Behavior and compliance:
   - Implement code so that all **JavaScript-based checks (`js:`)** evaluate to `true` 
     when the resulting page runs in a browser.
   - Satisfy any conditions mentioned in the `checks` — including DOM structure,
     CSS links (like `<link href*='bootstrap'>`), and computed dynamic values.
   - If a check includes formulas, like 
     `Math.abs(parseFloat(document.querySelector('#total-sales').textContent) - ${result}) < 0.01`,
     ensure your JavaScript logic dynamically computes matching values at runtime.
   - Include any required scripts or libraries (e.g., Bootstrap 5 from jsDelivr).
7. Format your output as a list of files, with each containing a file_name and file_content field
8. Do not include text explanations in the output; only return the code files and README as specified
9. Output format:
Return only a JSON array of objects where each object has:
- "file_name": string
- "file_content": string

The user will provide a brief describing the site functionality along with attachments (optional). Use these to guide your file generation.

Focus on quality, clarity, and correctness to deliver a ready-to-use GitHub Pages static website project.
"""

    try:
        agent = Agent(
            "openai:gpt-5-nano",
            result_type=List[FileContext],
            system_prompt=system_prompt
        )
        result = await agent.run(prompt)
        logger.info("Successfully generated code with LLM")
        # print(result.data)
        return result.data
    except Exception as e:
        # Log the error with traceback
        logger.error(f"Error generating code with LLM: {e}", exc_info=True)
        # Raise runtime error to caller or optionally return empty list/fallback output
        raise RuntimeError(f"LLM code generation failed: {e}") from e


async def round2_code_modification_function(
    files: List[FileContext],
    task_object: TaskRequest
) -> List[FileContext]:
    """
    Minimal Round 2 function - prevents loops by being ultra simple
    """
    print("Starting minimal Round 2 modification...")
    
    try:
        attachments_text = ""
        if task_object.attachments and len(task_object.attachments) > 0:
            attachments_text = "\nAttachments:\n" + "\n".join([f"- {att.name}: {att.url[:80]}..." for att in task_object.attachments])
        else:
            attachments_text = "\n(No attachments were provided with the request)"
        # Create simple file info for the AI
        
        files_str = "\n\n".join(
        [f"--- START FILE: {f.file_name} ---\n{f.file_content}\n--- END FILE: {f.file_name} ---" for f in files])

        # This is how you would create it in your Python function
# using f-strings.

        prompt = f"""
        **Objective:** Modify the following web project to satisfy the user's brief and pass all acceptance criteria.

        ---

        ### **User's Brief**

        "{task_object.brief}"

       ### **attachments given by user(if any)**

       "{attachments_text}

        ---

        ### **Acceptance Criteria (Checks)**

        The final code **MUST** pass all of the following checks. These are non-negotiable JavaScript expressions that will be evaluated in the browser's console. A failure to pass these checks means the task is a failure.

        {task_object.checks}



        ---

        ### **Project Files**

        Here are the complete contents of all files in the project. Analyze them and apply your changes where necessary.

        {files_str}

        ---

        **Final Instruction:**
        Perform the required modifications based on the brief and checks. Now, return the complete list of all project files in the required format.
        """
        
        
        
        simple_agent = Agent(
    "openai:gpt-5-nano",
    result_type=List[FileContext],
    system_prompt=""" You are an expert AI software developer specializing in frontend web technologies (HTML, CSS, and JavaScript). Your primary mission is to intelligently modify an existing codebase to fulfill a user's request while adhering to a strict set of rules.

**Your Core Directives:**

1.  **Principle of Minimal Change:** You must operate on the principle of minimal intervention. Your goal is to be a precise surgical tool, not a wrecking ball. Only make the changes necessary to satisfy the user's brief. Do not refactor, rewrite, or alter code that is not directly related to the task.

2.  **Preserve File Integrity:** Do not add or delete files from the project unless the user's brief explicitly and unambiguously instructs you to do so. The structure of the project must be maintained.

3.  **Completeness is Mandatory:** Your final output MUST include the complete content of ALL original files provided to you, even the files you did not modify. This is non-negotiable and ensures the entire project context is returned.

4.  **Strict Adherence to Checks:** The user will provide a list of "checks" (JavaScript expressions). The modified code must ensure that every single one of these expressions evaluates to `true`. These checks are your primary definition of success.

5.  **Focus on Static Deployment:** Assume the final code needs to be immediately deployable to a static hosting service like GitHub Pages. Do not introduce any server-side logic, dependencies, or build steps unless specifically requested.

6.  **No Conversational Output:** Do not provide explanations, apologies, or any conversational text in your final output. Your response must strictly be the structured data containing the list of files and their content.
    """
    
)
        
        # Run with strict limits to prevent loops
        result = await simple_agent.run(prompt)
        
        # print(result)
        return result.data
        
    except Exception as e:
        print(f"AI modification failed: {e}")
        print("Using text-based fallback...")






prompt="""
Analyze the existing codebase and implement the following requirement with minimal changes:

Requirements:
1. Make only targeted modifications to implement the new functionality
2. Do not rewrite entire files - add incrementally to existing code
3. Ensure all JavaScript validation checks pass
4. Update the README to document the changes
5. Maintain GitHub Pages compatibility
6. Preserve all existing functionality

Please analyze the code, understand the requirements, and provide the modified files.
"""


system_prompt="""You are an expert web developer tasked with making minimal, targeted modifications to an existing GitHub Pages codebase. 

Your responsibilities:
1. Analyze the existing code structure and functionality thoroughly
2. Make ONLY the minimal changes needed to implement the new brief requirements
3. Do NOT rewrite entire files or change the overall structure
4. Ensure all modifications will pass the provided JavaScript validation checks
5. Update the README file to reflect the changes made
6. Preserve all existing functionality while adding new features

Guidelines:
- Add new elements, functions, or styles incrementally
- Modify existing code only when absolutely necessary
- Test your changes against validation checks mentally before finalizing
- Keep the same coding style and patterns as the original code
- Focus on GitHub Pages compatibility (static HTML, CSS, JS only)"""
