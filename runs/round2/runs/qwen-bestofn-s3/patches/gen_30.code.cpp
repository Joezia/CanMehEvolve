
FIT_BOOL Mesg::HasField(const int fieldNum) const
{
    return std::find_if(fields.begin(), fields.end(), [fieldNum](const Field& f) {
        return f.GetNum() == fieldNum;
    }) != fields.end();
}
