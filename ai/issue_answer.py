from langchain.document_loaders.github import GitHubIssuesLoader
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnablePassthrough
from langchain.vectorstores import DocArrayInMemorySearch
from langchain.embeddings import OpenAIEmbeddings
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Your program description.")
    parser.add_argument("--github-token", required=True, help="GitHub access token")
    parser.add_argument("--openai-token", required=True, help="OpenAI API key")
    parser.add_argument("--issue-number", required=True, help="Github Issue Number")
    return parser.parse_args()

# Parse command line arguments
args = parse_arguments()

# Create an instance of the GitHubIssuesLoader class
loader = GitHubIssuesLoader(
    repo="XinShuYang/antrea",
    owner="XinShuYang",
    access_token=args.github_token,
    include_prs=False,
)

# Load the issues of the repository
issues = loader.load()

issue_data = []
# Print the title and body of each issue
for issue in issues:
    if issue.metadata["number"] == args.issue_number :
        issue_data.append({'title': issue.metadata['title'], 'body': issue.page_content})

vectorstore = DocArrayInMemorySearch.from_texts(
    ["The random error of layer can be preemptively avoided by adding checksum verification", "When local storage is depleted, Docker won't be able to load images properly","Not only the unnecessary antrea-agent, antea-cni binaries, but also the whole OVS, iptables, suricata dependecies can be got rid of from antrea-controller image"],
    embedding=OpenAIEmbeddings(openai_api_key=args.openai_token),
)
retriever = vectorstore.as_retriever()

template = """Analyze and give the solution of the github issue based only on the following context:
    {context}

GITHUB ISSUE: {question}
    """
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=args.openai_token)
output_parser = StrOutputParser()
setup_and_retrieval = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
)

chain = setup_and_retrieval | prompt | model | output_parser

result=chain.invoke(issue_data)

print(result)
