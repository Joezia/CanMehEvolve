FIT_UINT8 Field::GetNum(void) const
{
    if (__builtin_expect((profile != NULL) && (profileIndex < profile->numFields), 1))
        return profile->fields[profileIndex].num;
    return FIT_FIELD_NUM_INVALID;
}
