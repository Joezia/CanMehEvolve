FIT_UINT8 Field::GetNum(void) const
{
    if (__builtin_expect((profile == NULL) || (profileIndex >= profile->numFields), 0))
        return FIT_FIELD_NUM_INVALID;
    return profile->fields[profileIndex].num;
}
