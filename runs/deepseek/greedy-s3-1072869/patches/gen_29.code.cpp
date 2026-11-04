FIT_UINT8 Field::GetType() const
{
    const FIT_UINT8 fieldType = type;

    if (__builtin_expect(fieldType != FIT_UINT8_INVALID, 0))
    {
        return fieldType;
    }

    const auto fieldProfile = profile;
    if (__builtin_expect(fieldProfile == nullptr, 0) ||
        __builtin_expect(profileIndex >= fieldProfile->numFields, 0))
    {
        return fieldType;
    }

    return fieldProfile->fields[profileIndex].type;
}
