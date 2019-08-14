"""Integration test suite for analysis engine."""

import dacite
from pathlib import Path
import pytest

from coimbra_chamber.access.experiment.contracts import (
    FitSpec
)
from coimbra_chamber.access.experiment.models import (
    Fit
)

# ----------------------------------------------------------------------------
# Fixtures


# ----------------------------------------------------------------------------
# AnalysisEngine


def test_persist_fits(
        anlys_eng, mock_io_util, tube_spec, setting_spec, experiment_spec,
        observation_spec):  # noqa: D103
    # Arrange ----------------------------------------------------------------
    mock_io_util.get_input.return_value = ['c']
    # Use ExperimentAccess to add a tube, a setting, an experiment, and some
    # observations.
    access = anlys_eng._exp_acc
    _ = access._add_tube(tube_spec)
    setting_id = access._add_setting(setting_spec)
    experiment_id = access._add_experiment(experiment_spec, setting_id)
    _ = access._add_observations(observation_spec, experiment_id)
    # Setup a list of fits to add
    fits_to_add = []
    fit = dict(
        a=0.1, sig_a=0.01,
        b=-0.2, sig_b=0.02,
        r2=0.99,
        q=1e-8,
        chi2=9.5,
        nu_chi=11,
        exp_id=experiment_id,
        idx=0,
        mddp=12.0, sig_mddp=12.1,
        x1s=13.0, sig_x1s=13.1,
        x1e=14.0, sig_x1e=14.1,
        x1=15.0, sig_x1=15.1,
        m1s=16.0, sig_m1s=16.1,
        m1e=17.0, sig_m1e=17.1,
        m1=18.0, sig_m1=18.1,
        rhos=19.0, sig_rhos=19.1,
        rhoe=20.0, sig_rhoe=20.1,
        rho=21.0, sig_rho=21.1,
        Bm1=22.0, sig_Bm1=22.1,
        T=23.0, sig_T=23.1,
        D12=24.0, sig_D12=24.1,
        hfg=25.0, sig_hfg=25.1,
        hu=26.0, sig_hu=26.1,
        hs=27.0, sig_hs=27.1,
        cpv=28.0, sig_cpv=28.1,
        he=29.0, sig_he=29.1,
        cpl=30.0, sig_cpl=30.1,
        hT=31.0, sig_hT=31.1,
        qcu=32.0, sig_qcu=32.1,
        Ebe=33.0, sig_Ebe=33.1,
        Ebs=34.0, sig_Ebs=34.1,
        qrs=35.0, sig_qrs=35.1,
        kv=36.0, sig_kv=36.1,
        alpha=37.0, sig_alpha=37.1,
        Bh=38.0, sig_Bh=38.1,
        M=39.0, sig_M=39.1,
        gamma1=40.0, sig_gamma1=40.1,
        beta=41.0, sig_beta=41.1,
        Delta_m=42.0, sig_Delta_m=42.1,
        Delta_T=43.0, sig_Delta_T=43.1,
        mu=44.0, sig_mu=44.1,
        nu=45.0, sig_nu=45.1,
        gamma2=46.0, sig_gamma2=46.1,
        ShR=47.0, sig_ShR=47.1,
        NuR=48.0, sig_NuR=48.1,
        Le=49.0, sig_Le=49.1,
        GrR_binary=50.0, sig_GrR_binary=50.1,
        GrR_primary=51.0, sig_GrR_primary=51.1,
    )
    fits_to_add.append(fit)
    # Now the second one
    fit = dict(
        a=0.11, sig_a=0.011,
        b=-0.21, sig_b=0.021,
        r2=0.991,
        q=1.1e-8,
        chi2=9.51,
        nu_chi=111,
        exp_id=experiment_id,
        idx=1,
        mddp=121.0, sig_mddp=121.1,
        x1s=131.0, sig_x1s=131.1,
        x1e=141.0, sig_x1e=141.1,
        x1=151.0, sig_x1=151.1,
        m1s=161.0, sig_m1s=161.1,
        m1e=171.0, sig_m1e=171.1,
        m1=181.0, sig_m1=181.1,
        rhos=191.0, sig_rhos=191.1,
        rhoe=201.0, sig_rhoe=201.1,
        rho=211.0, sig_rho=211.1,
        Bm1=221.0, sig_Bm1=221.1,
        T=231.0, sig_T=231.1,
        D12=241.0, sig_D12=241.1,
        hfg=251.0, sig_hfg=251.1,
        hu=261.0, sig_hu=261.1,
        hs=271.0, sig_hs=271.1,
        cpv=281.0, sig_cpv=281.1,
        he=291.0, sig_he=291.1,
        cpl=301.0, sig_cpl=301.1,
        hT=311.0, sig_hT=311.1,
        qcu=321.0, sig_qcu=321.1,
        Ebe=331.0, sig_Ebe=331.1,
        Ebs=341.0, sig_Ebs=341.1,
        qrs=351.0, sig_qrs=351.1,
        kv=361.0, sig_kv=361.1,
        alpha=371.0, sig_alpha=371.1,
        Bh=381.0, sig_Bh=381.1,
        M=391.0, sig_M=391.1,
        gamma1=401.0, sig_gamma1=401.1,
        beta=411.0, sig_beta=411.1,
        Delta_m=421.0, sig_Delta_m=421.1,
        Delta_T=431.0, sig_Delta_T=431.1,
        mu=441.0, sig_mu=441.1,
        nu=451.0, sig_nu=451.1,
        gamma2=461.0, sig_gamma2=461.1,
        ShR=547.0, sig_ShR=547.1,
        NuR=548.0, sig_NuR=548.1,
        Le=549.0, sig_Le=549.1,
        GrR_binary=550.0, sig_GrR_binary=550.1,
        GrR_primary=551.0, sig_GrR_primary=551.1,
    )
    fits_to_add.append(fit)
    anlys_eng._fits = fits_to_add
    # Act --------------------------------------------------------------------
    num_fits_added = anlys_eng._persist_fits()
    # Assert -----------------------------------------------------------------
    assert num_fits_added == 2
    # Now query result -------------------------------------------------------
    session = access.Session()
    try:
        query = session.query(Fit).filter(Fit.experiment_id == 1)
        queried_fits = query.all()
        session.commit()
        assert len(queried_fits) == 2
        for fit in queried_fits:
            if fit.idx == 0:
                assert fit.a == 0.1
                assert fit.sig_a == 0.01
                assert fit.b == -0.2
                assert fit.sig_b == 0.02
                assert fit.r2 == 0.99
                assert fit.q == 1e-8
                assert fit.chi2 == 9.5
                assert fit.nu_chi == 11
                assert fit.mddp == 12
                assert fit.sig_mddp == 12.1
                assert fit.x1s == 13
                assert fit.sig_x1s == 13.1
                assert fit.x1e == 14
                assert fit.sig_x1e == 14.1
                assert fit.x1 == 15
                assert fit.sig_x1 == 15.1
                assert fit.m1s == 16
                assert fit.sig_m1s == 16.1
                assert fit.m1e == 17
                assert fit.sig_m1e == 17.1
                assert fit.m1 == 18
                assert fit.sig_m1 == 18.1
                assert fit.rhos == 19
                assert fit.sig_rhos == 19.1
                assert fit.rhoe == 20
                assert fit.sig_rhoe == 20.1
                assert fit.rho == 21
                assert fit.sig_rho == 21.1
                assert fit.Bm1 == 22
                assert fit.sig_Bm1 == 22.1
                assert fit.T == 23
                assert fit.sig_T == 23.1
                assert fit.D12 == 24
                assert fit.sig_D12 == 24.1
                assert fit.hfg == 25
                assert fit.sig_hfg == 25.1
                assert fit.hu == 26
                assert fit.sig_hu == 26.1
                assert fit.hs == 27
                assert fit.sig_hs == 27.1
                assert fit.cpv == 28
                assert fit.sig_cpv == 28.1
                assert fit.he == 29
                assert fit.sig_he == 29.1
                assert fit.cpl == 30
                assert fit.sig_cpl == 30.1
                assert fit.hT == 31
                assert fit.sig_hT == 31.1
                assert fit.qcu == 32
                assert fit.sig_qcu == 32.1
                assert fit.Ebe == 33
                assert fit.sig_Ebe == 33.1
                assert fit.Ebs == 34
                assert fit.sig_Ebs == 34.1
                assert fit.qrs == 35
                assert fit.sig_qrs == 35.1
                assert fit.kv == 36
                assert fit.sig_kv == 36.1
                assert fit.alpha == 37
                assert fit.sig_alpha == 37.1
                assert fit.Bh == 38
                assert fit.sig_Bh == 38.1
                assert fit.M == 39
                assert fit.sig_M == 39.1
                assert fit.gamma1 == 40
                assert fit.sig_gamma1 == 40.1
                assert fit.beta == 41
                assert fit.sig_beta == 41.1
                assert fit.Delta_m == 42
                assert fit.sig_Delta_m == 42.1
                assert fit.Delta_T == 43
                assert fit.sig_Delta_T == 43.1
                assert fit.mu == 44
                assert fit.sig_mu == 44.1
                assert fit.nu == 45
                assert fit.sig_nu == 45.1
                assert fit.gamma2 == 46.0
                assert fit.sig_gamma2 == 46.1
                assert fit.ShR == 47.0
                assert fit.sig_ShR == 47.1
                assert fit.NuR == 48.0
                assert fit.sig_NuR == 48.1
                assert fit.Le == 49.0
                assert fit.sig_Le == 49.1
                assert fit.GrR_binary == 50.0
                assert fit.sig_GrR_binary == 50.1
                assert fit.GrR_primary == 51.0
                assert fit.sig_GrR_primary == 51.1
            elif fit.idx == 1:
                assert fit.a == 0.11
                assert fit.sig_a == 0.011
                assert fit.b == -0.21
                assert fit.sig_b == 0.021
                assert fit.r2 == 0.991
                assert fit.q == 1.1e-8
                assert fit.chi2 == 9.51
                assert fit.nu_chi == 111
                assert fit.mddp == 121
                assert fit.sig_mddp == 121.1
                assert fit.x1s == 131
                assert fit.sig_x1s == 131.1
                assert fit.x1e == 141
                assert fit.sig_x1e == 141.1
                assert fit.x1 == 151
                assert fit.sig_x1 == 151.1
                assert fit.m1s == 161
                assert fit.sig_m1s == 161.1
                assert fit.m1e == 171
                assert fit.sig_m1e == 171.1
                assert fit.m1 == 181
                assert fit.sig_m1 == 181.1
                assert fit.rhos == 191
                assert fit.sig_rhos == 191.1
                assert fit.rhoe == 201
                assert fit.sig_rhoe == 201.1
                assert fit.rho == 211
                assert fit.sig_rho == 211.1
                assert fit.Bm1 == 221
                assert fit.sig_Bm1 == 221.1
                assert fit.T == 231
                assert fit.sig_T == 231.1
                assert fit.D12 == 241
                assert fit.sig_D12 == 241.1
                assert fit.hfg == 251
                assert fit.sig_hfg == 251.1
                assert fit.hu == 261
                assert fit.sig_hu == 261.1
                assert fit.hs == 271
                assert fit.sig_hs == 271.1
                assert fit.cpv == 281
                assert fit.sig_cpv == 281.1
                assert fit.he == 291
                assert fit.sig_he == 291.1
                assert fit.cpl == 301
                assert fit.sig_cpl == 301.1
                assert fit.hT == 311
                assert fit.sig_hT == 311.1
                assert fit.qcu == 321
                assert fit.sig_qcu == 321.1
                assert fit.Ebe == 331
                assert fit.sig_Ebe == 331.1
                assert fit.Ebs == 341
                assert fit.sig_Ebs == 341.1
                assert fit.qrs == 351
                assert fit.sig_qrs == 351.1
                assert fit.kv == 361
                assert fit.sig_kv == 361.1
                assert fit.alpha == 371
                assert fit.sig_alpha == 371.1
                assert fit.Bh == 381
                assert fit.sig_Bh == 381.1
                assert fit.M == 391
                assert fit.sig_M == 391.1
                assert fit.gamma1 == 401
                assert fit.sig_gamma1 == 401.1
                assert fit.beta == 411
                assert fit.sig_beta == 411.1
                assert fit.Delta_m == 421
                assert fit.sig_Delta_m == 421.1
                assert fit.Delta_T == 431
                assert fit.sig_Delta_T == 431.1
                assert fit.mu == 441
                assert fit.sig_mu == 441.1
                assert fit.nu == 451
                assert fit.sig_nu == 451.1
                assert fit.gamma2 == 461
                assert fit.sig_gamma2 == 461.1
                assert fit.ShR == 547.0
                assert fit.sig_ShR == 547.1
                assert fit.NuR == 548.0
                assert fit.sig_NuR == 548.1
                assert fit.Le == 549.0
                assert fit.sig_Le == 549.1
                assert fit.GrR_binary == 550.0
                assert fit.sig_GrR_binary == 550.1
                assert fit.GrR_primary == 551.0
                assert fit.sig_GrR_primary == 551.1
    finally:
        session.close()


def test_process_fits(anlys_eng, mock_io_util, tube_spec):  # noqa: D103
    # This is just a smoke test to make sure nothing breaks.
    mock_io_util.get_input.side_effect = [['f'], ['0', '3600'], ['c']]
    # Arrange ----------------------------------------------------------------
    # Update the engine's experiment_id.
    anlys_eng._experiment_id = 2
    # The anlys_eng has the following call mocked to return a serialized
    # DataSpec; see conftest.py.
    data = anlys_eng._exp_acc.get_raw_data('test_path')

    _ = anlys_eng._exp_acc._add_tube(tube_spec)
    _ = anlys_eng._exp_acc.add_raw_data(data)

    # This will be used in the assert phase.
    access = anlys_eng._exp_acc
    expected_indexes = [
        121, 268, 417, 570, 723, 876, 1033, 1192, 1355, 1514, 1679, 1844,
        2011, 2178, 2349, 2520, 2693, 2866, 3041, 3216, 3393,
    ]
    # Act --------------------------------------------------------------------
    anlys_eng.process_fits(data)
    # Assert -----------------------------------------------------------------
    # Here you need to query the fit table and make sure you get all of the
    # idx that you expected when.
    session = access.Session()
    try:
        result_indexes = [
            r.idx for r in
            session.query(Fit.idx)
            .filter(Fit.experiment_id == anlys_eng._experiment_id)
            .order_by(Fit.idx)
        ]
        session.commit()
        assert result_indexes == expected_indexes
    finally:
        session.close()
