FIT_UINT8 Field::GetNum(void) const
{
    const Profile* p = profile;
    return ((p != NULL) && (profileIndex < p->numFields))
               ? p->fields[profileIndex].num
               : static_cast<FIT_UINT8>(FIT_FIELD_NUM_INVALID);
}
