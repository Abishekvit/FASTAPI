def test_rag(authorized_client, test_documents):
    res = authorized_client.post(
        "/documents/rag",
        json={
            "query": "What is DummyFastAPI and who is 00929 ?",
            "limit": 5
        }
    )

    assert res.status_code == 200

    data = res.json()
    print(data)
    assert data["answer"]
    assert len(data["chunks"]) > 0

def test_unauthorized_rag(client):
    res = client.post(
        "/documents/rag",
        json={
            "query": "What is DummyFastAPI and who is 00929 ?",
            "limit": 5
        }
    )

    assert res.status_code == 401
def test_rag_with_wrong_query(authorized_client):
    res = authorized_client.post(
        "/documents/rag",
        json={
            "query": "",
            "limit": 5
        }
    )

    assert res.status_code == 400

# Make changes to code                 CI
# Commit changes  -------------------> Pull source code
#                                         Install Dependencies
#                                     Run Automated Tests       CD
#                                     Build Image ---------> Grabs Images
#                                                             Update Production
# Run Tests
# Build Image
# Deploy
# Left side is manual

#It is dead simple , you provide steps in yaml or json