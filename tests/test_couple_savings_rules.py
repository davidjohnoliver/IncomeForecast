import model
import couple_savings_rules


def test_equalizing_rrsp_only_split_partial():
    deltas = _get_updated_deltas_equalizing_rrsp_only_split(
        60000, 800, 0, 64000, 2100, 0, 110000
    )

    assert deltas.household_undifferentiated_savings == 14000

    assert deltas.partner1_deltas.rrsp == 5000
    assert deltas.partner2_deltas.rrsp == 9000


def test_equalizing_rrsp_only_split_all_partner1():
    deltas = _get_updated_deltas_equalizing_rrsp_only_split(
        72000, 0, 0, 57000, 0, 0, 117000
    )

    assert deltas.household_undifferentiated_savings == 12000

    assert deltas.partner1_deltas.rrsp == 12000
    assert deltas.partner2_deltas.rrsp == 0


def test_equalizing_rrsp_only_split_retired():
    deltas = _get_updated_deltas_equalizing_rrsp_only_split(
        0, 490000, 0, 0, 255000, 0, 70000
    )

    assert deltas.household_undifferentiated_savings == -70000

    assert deltas.partner1_deltas.rrsp == -35000
    assert deltas.partner2_deltas.rrsp == -35000


def test_equalizing_rrsp_only_split_retired_limited():
    deltas = _get_updated_deltas_equalizing_rrsp_only_split(
        0, 12000, 0, 0, 140000, 0, 63000
    )

    assert deltas.household_undifferentiated_savings == -63000

    assert deltas.partner1_deltas.rrsp == -12000
    assert deltas.partner2_deltas.rrsp == -51000


def _get_updated_deltas_equalizing_rrsp_only_split(
    partner1_gross_salary,
    partner1_rrsp_savings,
    partner1_tfsa_savings,
    partner2_gross_salary,
    partner2_rrsp_savings,
    partner2_tfsa_savings,
    household_spending,
):
    deltas = model.couple_deltas_state.from_year(1999)
    partner1_deltas = deltas.partner1_deltas.update_gross_salary(partner1_gross_salary)
    partner2_deltas = deltas.partner2_deltas.update_gross_salary(partner2_gross_salary)
    deltas = deltas.update_partner1_deltas(partner1_deltas)
    deltas = deltas.update_partner2_deltas(partner2_deltas)

    deltas = deltas.update_household_spending(household_spending)

    previous_deltas = model.couple_deltas_state.from_year(1998)
    previous_funds = model.couple_funds_state(
        model.funds_state(
            partner1_rrsp_savings, partner1_tfsa_savings, 1998, 0.0, 0.0, 0.0
        ),
        model.funds_state(
            partner2_rrsp_savings, partner2_tfsa_savings, 1998, 0.0, 0.0, 0.0
        ),
    )

    rule = couple_savings_rules.get_equalizing_rrsp_only_split()

    updated_deltas = rule(deltas, previous_funds, previous_deltas)

    return updated_deltas


def test_adjust_values_to_produce_sum():
    values_and_limits = [(5, 12), (2, 4), (0, 3), (0, 0)]
    target_sum = 10
    values_and_limits = couple_savings_rules._adjust_values_to_produce_sum(
        values_and_limits, target_sum
    )
    assert values_and_limits == [(6, 12), (3, 4), (1, 3), (0, 0)]


def test_adjust_values_to_produce_sum_no_valid_solution():
    values_and_limits = [(5, 12), (2, 4), (0, 3), (0, 0)]
    target_sum = 50
    values_and_limits = couple_savings_rules._adjust_values_to_produce_sum(
        values_and_limits, target_sum
    )
    assert values_and_limits == [(12, 12), (4, 4), (3, 3), (31, 0)]


def test_get_max_allowable_tfsa_contribution_with_withdrawal():
    # TFSA withdrawal should increase contribution room
    # We test this by looking at how the state is updated in model.py

    year = 2025
    previous_funds = model.funds_state(
        rrsp_savings=0,
        tfsa_savings=10000,
        year=year,
        unregistered_savings=0,
        tfsa_available_room=5000,  # Remaining room
        rrsp_available_room=0,
    )

    deltas = model.deltas_state.from_year(year + 1)
    deltas = deltas.update_tfsa(-2000)  # Withdrawal of 2000

    new_funds = model.get_updated_funds_from_deltas(previous_funds, deltas)

    # New room should be 5000 (old) + 2000 (withdrawn) = 7000
    assert new_funds.tfsa_available_room == 7000
    assert new_funds.tfsa_savings == 8000


def test_get_max_allowable_rrsp_contribution_with_withdrawal():
    # RRSP withdrawal should NOT increase contribution room

    year = 2025
    previous_funds = model.funds_state(
        rrsp_savings=10000,
        tfsa_savings=0,
        year=year,
        unregistered_savings=0,
        tfsa_available_room=0,
        rrsp_available_room=5000,  # Remaining room
    )

    deltas = model.deltas_state.from_year(year + 1)
    deltas = deltas.update_rrsp(-2000)  # Withdrawal of 2000

    new_funds = model.get_updated_funds_from_deltas(previous_funds, deltas)

    # New room should still be 5000
    assert new_funds.rrsp_available_room == 5000
    assert new_funds.rrsp_savings == 8000
