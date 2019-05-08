from pkg_resources import get_distribution
import subprocess


def get_git_version(path='.'):
    """
    Computes the version of a given git repository
    
    The version is computed assuming that the commit messages are formatted according 
    to SemVer and Conventional Commits. The version format is the following:
    
        <major>.<minor>.<patch>-r<release>
    
    The convention used here is the following
    - 'breaking:' types increase major version (rather than 'refactor:')
    - 'feat:' types increase minor version
    - 'fix:' types increase patch version
    - any other type that conforms to '<type>:' (where <type> can be chore, ci, test, ...)
    
    :param path: directory of the git repository (defaults to path)
    :return: The version number as a string
    """
    
    cmd = ['git', 'log', '--reverse','--pretty=oneline', path]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    major = 0
    minor = 0
    patch = 0
    release = 0

    for l in p.stdout:
        f = l.split()
        if len(f) >= 2:

            s = f[1].decode('utf-8')


            if s == 'breaking:':
                major += 1
                minor = 0
                patch = 0
                release = 0
                continue

            if s == 'feat:':
                minor += 1
                patch = 0
                release = 0
                continue

            if s == 'fix:':
                patch += 1
                release = 0
                continue

            if s.endswith(':'):
                release += 1

    ver = '{}.{}.{}'.format(major, minor, patch)
    if (release > 0):
        ver = ver + '-r{}'.format(release)
        
    return ver

if __name__ == "__main__":
    # determine version from git
    git_version = get_git_version()

    # monkey-patch `setuptools.setup` to inject the git version
    import setuptools
    original_setup = setuptools.setup

    def setup(version=None, *args, **kw):
        return original_setup(version=git_version, *args, **kw)

    setuptools.setup = setup

    # import the packages's setup module
    import setup
