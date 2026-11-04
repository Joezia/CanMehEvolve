FIT_UINT8 Field::GetNum(void) const
{
    if (__builtin_expect(profile == NULL, 0))
        return FIT_FIELD_NUM_INVALID;

    const FIT_UINT8 numFields = profile->numFields;
    const auto* fields = profile->fields;
    if (__builtin_expect(profileIndex >= numFields, 0))
        return FIT_FIELD_NUM_INVALID;

    return fields[profileIndex].num;
}
