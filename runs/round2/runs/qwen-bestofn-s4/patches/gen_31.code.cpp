Field* Mesg::GetField(const FIT_UINT8 fieldNum)
{
    const std::size_t size = fields.size();
    for (std::size_t i = 0; i < size; ++i) {
        if (fields[i].GetNum() == fieldNum) {
            return &fields[i];
        }
    }
    return FIT_NULL;
}
