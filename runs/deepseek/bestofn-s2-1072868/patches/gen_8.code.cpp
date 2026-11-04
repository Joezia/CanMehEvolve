Field* Mesg::GetFieldByIndex(const FIT_UINT16 index)
{
    return index < fields.size() ? fields.data() + index : FIT_NULL;
}
