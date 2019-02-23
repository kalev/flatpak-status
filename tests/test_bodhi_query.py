import responses

from flatpak_status.bodhi_query import list_updates, refresh_all_updates, refresh_updates
from flatpak_status.models import (Flatpak, FlatpakBuild, FlatpakUpdateBuild,
                                   Package, PackageBuild, PackageUpdateBuild)
from .bodhi import mock_bodhi
from .koji import make_koji_session


@responses.activate
def test_bodhi_query_package_updates(session):
    koji_session = make_koji_session()
    mock_bodhi()

    bubblewrap_package = Package.get_for_name(session, 'bubblewrap', koji_session=koji_session)

    refresh_updates(koji_session, session, 'rpm', packages=['bubblewrap'])

    updates = list_updates(session, 'rpm', bubblewrap_package)
    assert len(updates) == 3

    selected = [x for x in updates if x[0].build_nvr == 'bubblewrap-0.3.0-2.fc28']
    assert len(selected) == 1

    update_build, build = selected[0]
    assert isinstance(update_build, PackageUpdateBuild)
    assert update_build.build_nvr == 'bubblewrap-0.3.0-2.fc28'
    assert update_build.update.status == 'stable'
    assert isinstance(build, PackageBuild)
    assert build.nvr == 'bubblewrap-0.3.0-2.fc28'

    refresh_updates(koji_session, session, 'rpm', packages=['bubblewrap'])


@responses.activate
def test_bodhi_query_flatpak_updates(session):
    koji_session = make_koji_session()
    mock_bodhi()

    feedreader_flatpak = Flatpak.get_for_name(session, 'feedreader', koji_session=koji_session)

    refresh_all_updates(koji_session, session, 'flatpak')

    updates = list_updates(session, 'flatpak', feedreader_flatpak)
    assert len(updates) == 3

    selected = [x for x in updates if x[0].build_nvr == 'feedreader-master-2920190201225359.1']
    assert len(selected) == 1

    update_build, build = selected[0]
    assert isinstance(update_build, FlatpakUpdateBuild)
    assert update_build.build_nvr == 'feedreader-master-2920190201225359.1'
    assert update_build.update.status == 'obsolete'
    assert isinstance(build, FlatpakBuild)
    assert build.nvr == 'feedreader-master-2920190201225359.1'

    refresh_all_updates(koji_session, session, 'flatpak')
