FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 cachedType = type;
    if (cachedType != FIT_UINT8_INVALID)
        return cachedType;

    const auto* const cachedProfile = profile;
    if (cachedProfile == NULL)
        return FIT_UINT8_INVALID;

    const FIT_UINT8 cachedIndex = profileIndex;
    if (cachedIndex >= cachedProfile->numFields)
        return FIT_UINT8_INVALID;

    return cachedProfile->fields[cachedIndex].type;
}
