FIT_UINT8 Field::GetNum(void) const
{
    if (__builtin_expect(profile == NULL, 0))
        return FIT_FIELD_NUM_INVALID;

    if (__builtin_expect(profileIndex >= profile->numFields, 0))
        return FIT_FIELD_NUM_INVALID;

    return profile->fields[profileIndex].num;
}
