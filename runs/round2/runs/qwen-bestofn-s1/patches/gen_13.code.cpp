
FIT_UINT8 Field::GetNum(void) const
{
    // Early return for common case: profile is non-null and index is within bounds
    // Avoid repeated member access by caching profile pointer
    const Profile* p = profile;
    if (p == nullptr || profileIndex >= p->numFields) {
        return FIT_FIELD_NUM_INVALID;
    }
    return p->fields[profileIndex].num;
}
