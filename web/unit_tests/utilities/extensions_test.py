from src.utilities.extensions import Extensions
from src.models.model import File

def test_get_extensions():
    # arrange
    files = [
        File(id='...', name='abc.py', commit_id='...'),
        File(id='...', name='def.js', commit_id='...'),
        File(id='...', name='hij.c', commit_id='...'),
        File(id='...', name='klm.php', commit_id='...'),
        File(id='...', name='nop.xml', commit_id='...'),
        File(id='...', name='qrs', commit_id='...'),
    ]

    # act
    extensions = Extensions.get_extension_set(files)

    # assert
    assert ".py" in extensions
    assert ".js" in extensions
    assert ".c" in extensions
    assert ".php" in extensions
    assert ".xml" in extensions
    return