
Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    for (auto& f : fields) {
        if (f.GetNum() == fieldNum) {
            return &f;
        }
    }
    return FIT_NULL;
}
