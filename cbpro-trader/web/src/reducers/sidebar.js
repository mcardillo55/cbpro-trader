const sidebar = (state = {indicators: [], flags: {}, balances: {}, orders: {'fills': [], 'orders': []},
                          primary_section: "periods", secondary_section: "details"}, action) => {
    switch (action.type) {
        case 'CHANGE_PRIMARY_SECTION':
            return {
                ...state,
                primary_section: action.section_name
            }
        case 'CHANGE_SECONDARY_SECTION':
            return {
                ...state,
                secondary_section: action.section_name
            }
        case 'UPDATE_BALANCES':
            return {
                ...state,
                balances: action.balances
            }
        case 'UPDATE_INDICATORS':
            return {
                ...state,
                indicators: action.indicators
            }
        case 'UPDATE_FLAGS':
            return {
                ...state,
                flags: action.flags
            }
        case 'UPDATE_ORDERS':
            return {
                ...state,
                orders: action.orders
            }
        default:
            return state
    }
}

export default sidebar;