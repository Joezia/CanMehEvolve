FIT_UINT8 Field::GetNum(void) const
{
    static const decltype(profile->numFields) zero = 0;
    const auto *numFields = profile ? &profile->numFields : &zero;
    if (profileIndex >= *numFields)
        return FIT_FIELD_NUM_INVALID;
    return profile->fields[profileIndex].num;
}
