from modules.xml_tools import XMLScheduleReader
import os

def test_xml_parsing():
    # Use relative path from where we run the script
    xml_path = "../sample_project.xml"

    with open(xml_path, 'r') as f:
        # Mocking the file object behavior for read()
        class MockFile:
            def __init__(self, content):
                self.content = content
            def read(self):
                return self.content

        file_obj = MockFile(f.read())

    df = XMLScheduleReader.parse_xml(file_obj)

    print("Columns:", df.columns)
    print("Rows:", len(df))
    print(df.head())

    assert not df.empty
    assert len(df) == 3
    assert "Name" in df.columns
    assert df.iloc[0]["Name"] == "Design Phase"
    assert df.iloc[0]["PercentComplete"] == 100

    # Check resources
    resources = df.iloc[1]["Resources"] # Development Phase has Alice and Bob
    print("Resources for Task 2:", resources)
    assert "Alice" in resources
    assert "Bob" in resources

if __name__ == "__main__":
    test_xml_parsing()
