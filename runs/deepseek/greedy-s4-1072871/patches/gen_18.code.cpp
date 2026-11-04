FIT_UINT8 Field::GetNum(void) const
{
    if (__builtin_expect(profile == NULL, 0))
        return FIT_FIELD_NUM_INVALID;
    const FIT_UINT8 index = profileIndex;
    if (__builtin_expect(index >= profile->numFields, 0))
        return FIT_FIELD_NUM_INVALID;
    return profile->fields[index].num;
}
